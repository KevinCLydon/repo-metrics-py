import logging

import requests

from ..settings import Settings


class GitHubException(Exception):
    pass


LOGGER = logging.getLogger(__name__)


class GitHubMetricsHelper:
    """
    A helper class for getting metrics from the GitHub API
    """

    def __init__(self):
        # Get the GitHub API token from the environment variable (if there is one)
        token = Settings().get_github_token()
        self.token: str | None = token

    def get_repo_info(self, owner: str, repo: str) -> dict:
        """
        Get info for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: A dictionary containing the repository info
        """
        url = f"https://api.github.com/repos/{owner}/{repo}"
        if self.token:
            headers = {"Authorization": f"token {self.token}"}
        else:
            headers = {}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise GitHubException(f"Failed to get info for {owner}/{repo}")
        data = response.json()

        # Get the download count for the repository
        download_count = self.__get_download_count(owner, repo)
        data["download_count"] = download_count

        return data

    def get_release_download_counts(self, owner: str, repo: str) -> dict:
        """
        Get download counts for all releases in the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: A dictionary containing the download counts for each release
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        if self.token:
            headers = {"Authorization": f"token {self.token}"}
        else:
            headers = {}

        release_download_counts = {}

        # Paginate through the releases to get the download counts
        page = 1
        while True:
            # Set the per_page parameter to 100 to get the maximum number of releases per page
            params = {"page": page, "per_page": 100}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubException(f"Failed to get info for {owner}/{repo}")
            releases = response.json()

            # If there are no more releases, break out of the loop
            if not releases:
                break

            for release in releases:
                release_name = release["tag_name"]
                download_count = 0
                for asset in release["assets"]:
                    download_count += asset["download_count"]
                release_download_counts[release_name] = download_count

            page += 1

        return release_download_counts

    def __get_download_count(self, owner: str, repo: str) -> int:
        """
        Get the download count for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: The download count
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        if self.token:
            headers = {"Authorization": f"token {self.token}"}
        else:
            headers = {}

        # Paginate through the releases to get the download count
        page = 1
        download_count = 0
        while True:
            # Set the per_page parameter to 100 to get the maximum number of releases per page
            params = {"page": page, "per_page": 100}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubException(f"Failed to get info for {owner}/{repo}")
            releases = response.json()

            # If there are no more releases, break out of the loop
            if not releases:
                break

            for release in releases:
                for asset in release["assets"]:
                    download_count += asset["download_count"]

            page += 1

        return download_count
