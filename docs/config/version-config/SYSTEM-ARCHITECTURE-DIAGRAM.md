graph TB
    subgraph "HypatiaX Root Directory"
        ROOT[hypatiax/]
        
        subgraph "Version Management Scripts"
            SCRIPTS[scripts/version_management/]
            
            subgraph "Core System"
                GVM[global_version_manager.py<br/>Main version tracking]
                VI[version_injector.py<br/>Environment injection]
                VL[version_loader.py<br/>Auto-generated loader]
            end
            
            subgraph "Utilities"
                VS[version_status.sh<br/>Status checker]
                RV[restore_version.sh<br/>Restore helper]
            end
            
            subgraph "Workflows"
                DU[daily_version_update.sh<br/>Daily workflow]
                PTS[pre_training_snapshot.sh<br/>Pre-training]
                POV[post_training_version.sh<br/>Post-training]
            end
            
            subgraph "Configuration"
                CFG[example.env.versions<br/>Config examples]
            end
        end
        
        subgraph "Version Storage"
            VDIR[.versions/]
            GMETA[global_versions.json<br/>Metadata]
            VCFG[version_config.json<br/>Config]
            SNAP[snapshots/<br/>Complete backups]
            VDATA[Versioned data by type]
        end
        
        subgraph "Generated Files"
            ENV[.env.versions<br/>Environment vars]
            LOADER[version_loader.py<br/>Python module]
        end
        
        subgraph "Project Data"
            RULES[custom_ner/rules/<br/>Rule files]
            TRAIN[datasets/training/<br/>Training data]
            TEST[datasets/testing/<br/>Test data]
            MODELS[data_spacy/<br/>Trained models]
        end
        
        subgraph "GitHub Integration"
            GHA[.github/workflows/<br/>Actions]
            VMWF[version-management.yml<br/>Main workflow]
        end
    end
    
    %% Core System Relationships
    GVM -->|Creates/Manages| VDIR
    GVM -->|Updates| GMETA
    GVM -->|Creates| SNAP
    GVM -->|Scans| RULES
    GVM -->|Scans| TRAIN
    GVM -->|Scans| MODELS
    
    VI -->|Reads| GMETA
    VI -->|Updates| VCFG
    VI -->|Generates| ENV
    VI -->|Generates| LOADER
    
    %% Workflow Relationships
    DU -->|Calls| GVM
    DU -->|Calls| VI
    DU -->|Updates| ENV
    
    PTS -->|Calls| GVM
    POV -->|Calls| GVM
    POV -->|Calls| VI
    
    %% Utility Relationships
    VS -->|Calls| VI
    VS -->|Calls| GVM
    RV -->|Calls| GVM
    
    %% GitHub Actions
    VMWF -->|Triggers| DU
    VMWF -->|Triggers| GVM
    VMWF -->|Uploads| SNAP
    
    %% User Interactions
    USER[👤 User] -->|Runs| VS
    USER -->|Runs| DU
    USER -->|Runs| PTS
    USER -->|Runs| POV
    USER -->|Loads| ENV
    
    PYTHON[🐍 Python Scripts] -->|Imports| LOADER
    PYTHON -->|Reads| ENV
    
    %% Styling
    classDef coreClass fill:#4A90E2,stroke:#2E5C8A,stroke-width:2px,color:#fff
    classDef utilClass fill:#50C878,stroke:#2E7D50,stroke-width:2px,color:#fff
    classDef workflowClass fill:#9B59B6,stroke:#6C3D7A,stroke-width:2px,color:#fff
    classDef dataClass fill:#F39C12,stroke:#B8730D,stroke-width:2px,color:#fff
    classDef ghaClass fill:#E74C3C,stroke:#A93629,stroke-width:2px,color:#fff
    classDef userClass fill:#34495E,stroke:#1C2833,stroke-width:2px,color:#fff
    
    class GVM,VI,VL coreClass
    class VS,RV utilClass
    class DU,PTS,POV workflowClass
    class VDIR,GMETA,VCFG,SNAP,ENV,LOADER,RULES,TRAIN,MODELS dataClass
    class GHA,VMWF ghaClass
    class USER,PYTHON userClass