# Utilities like clean_domain(), domain_to_root_url() 

from urllib.parse import urlparse


def clean_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # remove classical subdomains
        parts = domain.split('.')
        if len(parts) > 2:
            domain = '.'.join(parts[-2:])
        return domain
    except:  # noqa: E722
        return None

#def remove_existing_domains(url):

def domain_to_root_url(domain):
    """
    Convert a domain (e.g., 'codesandbox.io') to a full root URL (e.g., 'https://codesandbox.io').

    :param domain: The domain name (e.g., 'codesandbox.io')
    :return: The full root URL (e.g., 'https://codesandbox.io')
    """
    # Ensure the domain is not empty and strip any leading/trailing spaces
    domain = domain.strip()
    
    # Check if the domain already has a protocol (http or https)
    if not domain.startswith(('http://', 'https://')):
        # If no protocol is found, prepend 'https://'
        domain = 'https://' + domain
    
    # Return the URL with the domain as the root URL
    return domain
