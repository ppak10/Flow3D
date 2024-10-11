from huggingface_hub import HfApi, upload_folder

version = 0

class HuggingFace():
    """
    Huggingface hub related api endpoint methods.
    """

    def __init__(self):
        self.api = HfApi()
    
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
        repo_exists = self.api.repo_exists(repo_id, repo_type=repo_type)

        if repo_exists:
            if delete_existing:
                # Delete existing repo on HuggingFace
                try:
                    self.api.delete_repo(repo_id, repo_type=repo_type)
                except Exception as e:
                    # It is possible that this error occurs when repo is renamed.
                    print(e)
            else:
                return "repo exists"
            
        repo_url = self.api.create_repo(
            repo_id,
            repo_type=repo_type,
            private=private
        )

        self.api.add_collection_item(
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
    