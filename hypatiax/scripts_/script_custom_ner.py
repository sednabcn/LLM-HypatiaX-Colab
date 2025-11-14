import os
import pandas as pd

from hypatiax.custom_ner.custom_ruler import CustomNerComponent

def get_ner_component(domain,sub_domain,type,python_version):
    
    component = CustomNerComponent(doamin,sub_domain,type,python_version)
    output = component.get_entity_ruler()
    return output

if __name__=='__main__':
     get_ner_component('queries','tableau','desc','python3.12')
     get_ner_component('queries','tableau','formulas','python3.12')
     get_ner_component('queries','tableau','both','python3.12')
   
     
