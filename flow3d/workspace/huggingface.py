from huggingface_hub import HfApi, upload_folder

hf_api = HfApi()

class WorkspaceHuggingFace():
    """
    Workspace Huggingface hub related api endpoint methods.
    """

    def workspace_dataset_initialize(self,
                                     dataset_id=None,
                                     private=False,
                                     format="huggingface",
                                     ):

        # Create Huggingface Dataset (if non-existant)
        if dataset_id == None:
            dataset_id = self.filename

        if format == "huggingface":
            # TODO: Implement check for existing repo.
            # Will need to dataset_id with org or user id in order to make this
            # work properly.
            # repo_exists = hf_api.repo_exists(repo_id = dataset_id, repo_type="dataset")
            repo_url = hf_api.create_repo(
                repo_id = dataset_id,
                repo_type = "dataset",
                private=private
            )
            print(f"Created new dataset at: {repo_url}")

    workspace_dataset_init = workspace_dataset_initialize
    
    def create_repo_and_add_collection_item(
        self,
        repo_id,
        collection_slug,
        repo_type = "dataset",
        delete_existing = False,
        private = False
    ):
        """
        Wrapper for creating repository and adding it to collection.
        """

        # Check if repo exists
        repo_exists = hf_api.repo_exists(repo_id, repo_type=repo_type)

        if repo_exists:
            if delete_existing:
                # Delete existing repo on HuggingFace
                try:
                    hf_api.delete_repo(repo_id, repo_type=repo_type)
                except Exception as e:
                    # It is possible that this error occurs when repo is renamed.
                    print(e)
            else:
                return "repo exists"
            
        repo_url = hf_api.create_repo(
            repo_id,
            repo_type=repo_type,
            private=private
        )

        hf_api.add_collection_item(
            collection_slug,
            item_id=repo_id,
            item_type=repo_type 
        )

        return repo_url

    @staticmethod 
    def upload_folder(repo_id, folder_path, path_in_repo, repo_type="dataset"):
        """
        https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api#huggingface_hub.HfApi.upload_folder
        """
        return upload_folder(
            repo_id = repo_id,
            folder_path = folder_path,
            path_in_repo = path_in_repo,
            repo_type = repo_type
        )
    