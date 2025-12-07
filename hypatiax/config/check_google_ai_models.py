from google.cloud import aiplatform_v1

project = "genai-412810"
location = "us-central1"

# Initialize the AI Platform client
client = aiplatform_v1.ModelServiceClient()
parent = f"projects/{project}/locations/{location}"

print("Listing Vertex AI models...")
models = client.list_models(parent=parent)

for model in models:
    print(model.name, model.display_name)
