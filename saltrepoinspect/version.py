import re
import os
import requests
from bs4 import BeautifulSoup


def parse_version(version):
    exp = '(?P<vendor>sles|rhel)(?P<major>\d{1,})(?:(?P<sp>sp)(?P<minor>\d{1,}))*'
    return re.match(exp, version).groups()


def parse_flavor(flavor):
    flavor_major = None
    flavor_minor = None

    if flavor == 'devel':
        # devel means install salt from git repository
        # and because there are no OBS repositories for it
        # we treat it as products so that we don't break the templates commands
        flavor_major = 'products'
    else:
        splitted = flavor.split('-')
        if len(splitted) == 1:
            flavor_major, flavor_major_sec, flavor_minor = flavor, None, None
        elif len(splitted) == 2:
            flavor_major, flavor_major_sec, flavor_minor = splitted[0], None, splitted[1]
        elif len(splitted) == 3:
            flavor_major, flavor_major_sec, flavor_minor = splitted

    return flavor_major, flavor_major_sec, flavor_minor


def get_salt_version(version, flavor):
    salt_repo_url = get_salt_repo_url(version, flavor)
    resp = requests.get("{0}/x86_64".format(salt_repo_url))
    if not resp.status_code == 200:
        return 'n/a'
    soup = BeautifulSoup(resp.content, 'html.parser')
    ex = re.compile(r'^salt-(?P<version>[0-9\.]+)-(?P<build>[0-9\.]+).x86_64.rpm$')
    salt = soup.find('a', text=ex)
    if not salt:
        return 'n/a'
    match = ex.match(salt.text)
    return match.groupdict()['version']


def get_repo_parts(version):
    vendor, version_major, separator, version_minor = parse_version(version)
    repo_parts = [version_major]
    if version_minor:
        repo_parts.append('{0}{1}'.format(separator, version_minor))
    return repo_parts


def get_repo_name(version, flavor):
    vendor, version_major, separator, version_minor = parse_version(version)
    repo_parts = get_repo_parts(version)
    if vendor == 'SLES' and version_major == '11':
        repo_name = 'SLE_11_SP4'
    else:
        repo_name = '_'.join(repo_parts)
    return repo_name


def get_salt_repo_name(version, flavor):
    vendor, version_major, separator, version_minor = parse_version(version)
    repo_name = get_repo_name(version, flavor)
    salt_repo_name = 'SLE_{0}'.format(repo_name).upper()
    if vendor == 'rhel':
        salt_repo_name = '{0}_{1}'.format(vendor, repo_name)

    if version in ['sles11sp3', 'sles11sp4']:
        salt_repo_name = 'SLE_11_SP4'

    return salt_repo_name


def get_salt_repo_url_flavor(flavor):
    flavor_major, flavor_major_sec, flavor_minor = parse_flavor(flavor)
    salt_repo_url_parts = [flavor_major]
    if flavor_major_sec:
        salt_repo_url_parts.append(flavor_major_sec)
    if flavor_minor:
        salt_repo_url_parts.append(flavor_minor)
    salt_repo_url_flavor = ':/'.join(salt_repo_url_parts)
    return salt_repo_url_flavor



def get_salt_repo_url(version, flavor):
    salt_repo_url_flavor = get_salt_repo_url_flavor(flavor)
    salt_repo_name = get_salt_repo_name(version, flavor)
    salt_repo_url = os.environ.get(
        "SALT_REPO_URL",
        "http://{0}/repositories/systemsmanagement:/saltstack:/{1}/{2}/".format(
            os.environ.get("MIRROR", "download.opensuse.org"),
            salt_repo_url_flavor,
            salt_repo_name.upper()
        )
    )
    return salt_repo_url


def get_docker_params(version, flavor):
    vendor, version_major, separator, version_minor = parse_version(version)
    flavor_major, flavor_major_sec, flavor_minor = parse_flavor(flavor)
    repo_name = get_repo_name(version, flavor)
    salt_repo_name = get_salt_repo_name(version, flavor)
    salt_repo_url_flavor = get_salt_repo_url_flavor(flavor)
    repo_parts = get_repo_parts(version)
    novel_repo_name = '-'.join(repo_parts).upper()
    parent_image = 'registry.mgr.suse.de/{0}'.format(version)
    repo_label = ' '.join(repo_parts).upper()
    salt_repo_url = get_salt_repo_url(version, flavor)
    salt_version = get_salt_version(version, flavor)

    return dict(
        vendor = vendor,
        major=version_major,
        minor=version_minor,
        version_separator=separator,
        flavor=flavor,
        version=version,
        parent_image=parent_image,
        flavor_major=flavor_major,
        flavor_major_sec=flavor_major_sec,
        flavor_minor=flavor_minor,
        repo_name=repo_name,
        novel_repo_name=novel_repo_name,
        repo_label=repo_label,
        salt_repo_url_flavor=salt_repo_url_flavor,
        salt_repo_name=salt_repo_name,
        salt_repo_url=salt_repo_url,
        salt_version=salt_version)
