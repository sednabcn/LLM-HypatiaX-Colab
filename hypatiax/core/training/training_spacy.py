#/usr/bin/python3
# write all options of these training models according using ner_entities or pre-trained ner_entities
# save fig of history plotting
import os
import spacy
import random
import pandas as pd
import time
from importlib import resources
from spacy.util import minibatch, compounding
from spacy.training import Example
from spacy.tokens import DocBin
from matplotlib import pyplot as plt
(year,month,day,hr,minutes,sec,_,_,_)=time.localtime()

class Training:
    def __init__(self,domain,sub_domain,train_data,dtype, output_model_name,niter, drop, batchsize,patience=10, n_checkpoint=50,val_data=None, option=None):
        self.domain=domain
        self.sub_domain=sub_domain
        self.train_data = train_data
        self.path_ner_model = resources.files(f'hypatiax.data_spacy.{domain}.{sub_domain}').joinpath(f'ner_{sub_domain}_{dtype}')
        self.output_model=f'{output_model_name}_{sub_domain}_{niter}_{drop}_{batchsize}_data'  
        self.niter = niter
        self.drop = drop
        self.batchsize = batchsize
        self.n_checkpoint=n_checkpoint
        self.val_data = val_data
        self.option = option
        self.stime=f'{year}_{month)_{day}_{hr}_{minutes}_{sec}'
        self.path_dir = resources.files(f'hypatiax.models.{domain}.{sub_domain}'}
        self.patience=patience #number of iterations to allow no improvement
        if dtype=="both":
            self.path_ner_model = resources.files(f'hypatiax.data_spacy.{domain}.{sub_domain}').joinpath(f'ner_{sub_domain}')
        # Ensure train_data is correctly assigned for multitask options
        if isinstance(train_data, list) and len(train_data) == 2:
            self.training_data_1 = train_data[0]
            self.training_data_2 = train_data[1]
        elif isinstance(train_data, list):
            self.training_data = train_data
        else:
            raise ValueError("Invalid training data provided")
        
    def train(self):
        # Method dispatch based on whether we have multitask training or not
        if hasattr(self, 'training_data_1') and hasattr(self, 'training_data_2'):
            return self.training_data_multitask()
        else:
            return self.training_data()

    def training_data(self):
        nlp = spacy.load(self.path_ner_model)
        ner = nlp.get_pipe('ner')
        for _, annotations in self.train_data:
            for ent in annotations.get('entities'):
                ner.add_label(ent[2])
        examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in self.train_data]
        examples_val = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in self.val_data] if self.val_data else None
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        history = pd.DataFrame(columns=['Iteration', 'Training Loss', 'Validation Loss' if self.val_data else ''])
        best_loss = float('inf')
        no_improve = 0  # Counter for early stopping

        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.resume_training()
            for i in range(self.niter):
                random.shuffle(examples)
                batches = minibatch(examples, size=self.batchsize)
                losses = {}
                for batch in batches:
                    nlp.update(batch, drop=self.drop, losses=losses, sgd=optimizer)
            
                if self.val_data:
                    val_losses = {}
                    for example in examples_val:
                        nlp.update([example], drop=0, sgd=None, losses=val_losses)
                    validation_loss = val_losses['ner']
                    history.loc[i] = [i, losses['ner'], validation_loss]
                    print(f"Iteration {i}, Training Loss: {losses['ner']}, Validation Loss: {validation_loss}")
                
                    if validation_loss < best_loss:
                        best_loss = validation_loss
                        best_model_path = os.path.join(self.path_dir,'trained_models',self.output_model"-best_model-" + str(self.stime))
                        nlp.to_disk(best_model_path)
                        history_model_path=os.path.join(self.path_dir,'training_history','history_'+self.output_model + '_' + str(self.stime))
                        history.to_excel(history_model_path)
                        print("Best model saved at iteration", i)
                        no_improve = 0  # Reset counter
                    else:
                        no_improve += 1

                    if no_improve >= self.patience:
                        print(f"Early stopping at iteration {i} due to no improvement in validation loss.")
                        break
                    
                else:
                    history.loc[i] = [i, losses['ner']]
                    print(f"Iteration {i}, Training Loss: {losses['ner']}")

                if i % self.n_checkpoint == 0:  # Save every 10 iterations
                    checkpoint_dir = os.path.join(self.path_dir,'checkpoints', + 'checkpoint_'+str(self.stime)+f'{i}')
                    nlp.to_disk(checkpoint_dir)

                    history_model_path_=os.path.join(self.path_dir,'training_history','history_'+self.output_model + '_' + str(self.stime) + f'{i}')
                    history.to_excel(history_model_path_)

    return history, nlp

    def training_data_multitask(self):
        nlp = spacy.load(self.path_ner_model)
        examples_ner1 = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in self.training_data_1]
        examples_ner2 = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in self.training_data_2]
        examples_val = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in self.val_data] if self.val_data else None
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        history = pd.DataFrame(columns=['Iterations', 'Training Loss', 'Validation Loss' if self.val_data else ''])
        best_loss =float('inf')
        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.resume_training()
            for i in range(self.niter):
                random.shuffle(examples_ner1)
                random.shuffle(examples_ner2)
                losses = {}
                if self.option == "1":
                    batches = minibatch(examples_ner1 + examples_ner2, size=self.batchsize)
                    for batch in batches:
                        nlp.update(batch, drop=self.drop, losses=losses, sgd=optimizer)
                elif self.option == "2":
                    batch_sizes = compounding(4., self.batchsize, 1.001)
                    batches_ner1 = minibatch(examples_ner1, size=batch_sizes)
                    batches_ner2 = minibatch(examples_ner2, size=batch_sizes)
                    for batch_ner1, batch_ner2 in zip(batches_ner1, batches_ner2):
                        nlp.update(batch_ner1, drop=self.drop, losses=losses, sgd=optimizer)
                        nlp.update(batch_ner2, drop=self.drop, losses=losses, sgd=optimizer)
                else:
                    continue  # No operation defined for other options

                # Calculate and log validation loss if validation data is provided
                
                if self.val_data:
                    val_losses = {}
                    for example in examples_val:
                        nlp.update([example], drop=0, sgd=None, losses=val_losses)
                    validation_loss = val_losses['ner']
                    history.loc[i] = [i, losses['ner'], validation_loss]
                    print(f"Iteration {i}, Training Loss: {losses['ner']}, Validation Loss: {validation_loss}")

                    if validation_loss < best_loss:
                        best_loss = validation_loss
                        best_model_path = os.path.join(self.path_dir,'trained_models',self.output_model"-best_model-" + str(self.stime))
                        
                        nlp.to_disk(best_model_path)
                        history_model_path=os.path.join(self.path_dir,'training_history','history_'+self.output_model + '_' + str(self.stime))
                        history.to_excel(history_model_path)
                        print("Best model saved at iteration", i)
                        no_improve = 0  # Reset counter
                    else:
                         no_improve += 1

                    if no_improve >= self.patience:
                        print(f"Early stopping at iteration {i} due to no improvement in validation loss.")
                        break
                    

                else:
                    history.loc[i] = [i, losses['ner']]
                    print(f"Iteration {i}, Training Loss: {losses['ner']}")

                if i % self.n_checkpoint == 0:  # Save every 10 iterations
                    checkpoint_dir = os.path.join(self.path_dir,'checkpoints', + 'checkpoint_'+str(self.stime)+f'{i}')
                  
                    nlp.to_disk(checkpoint_dir)

                     history_model_path_=os.path.join(self.path_dir,'training_history','history_'+self.output_model + '_' + str(self.stime) + f'{i}')
                    history.to_excel(history_model_path_)

        return history,nlp

    def save_model(self):
        model_path = os.path.join(self.path_dir,'trained_models',self.output_model+ str(self.stime))
        nlp.to_disk(model_path)

    def plot_history(self, history):
        plt.figure()
        if 'Validation Loss' in history.columns:
            plt.plot(history['Iterations'], history['Training Loss'], label='Training Loss')
            plt.plot(history['Iterations'], history['Validation Loss'], label='Validation Loss')
            plt.title('Training and Validation Losses over Iterations')
            plt.ylabel('Loss')
            plt.legend()
        else:
            plt.plot(history['Iterations'], history['Training Loss'], label='Training Loss')
            plt.title('Training Loss over Iterations')
            plt.ylabel('Loss')

        plt.xlabel('Iterations')

        # Define the output directory
        output_dir = self.path_dir  # Assume self.path_dir is set and is the directory you want to use
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the plot
        plt.savefig(os.path.join(output_dir,'training_history', f"figure_{self.niter}_{self.drop}_{self.batchsize}_{self.stime}.png"))

        # Show the plot
        plt.show()
  

