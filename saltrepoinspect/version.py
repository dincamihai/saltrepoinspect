import re
import requests
from bs4 import BeautifulSoup


def get_salt_version(repo_url):
    resp = requests.get("{0}/x86_64".format(repo_url))
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'html.parser')
    ex = re.compile(r'^salt-(?P<version>[0-9a-z-\.]+)-(?P<build>[0-9\.]+).x86_64.rpm')
    salt = soup.find('a', href=ex)
    match = ex.match(salt.text)
    return match.groupdict()['version']
