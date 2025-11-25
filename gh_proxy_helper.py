import re
def set_gh_proxy(config, selected_index=0):

    proxy_methods = [
        ("gh-proxy.com", "https://gh-proxy.com/"),
        ("gh.sageer.me", "https://gh.sageer.me/"),
        ("ghproxy.com", "https://ghproxy.com/"),
        ("mirror.ghproxy.com", "https://mirror.ghproxy.com/"),
        ("jsDelivr", "jsdelivr"),
        ("jsDelivr CF", "testingcf.jsdelivr.net"),
        ("jsDelivr Fastly", "fastly.jsdelivr.net"),
    ]

    selected_name, selected_prefix = proxy_methods[selected_index]
    all_prefixes = [prefix for _, prefix in proxy_methods]

    def restore_raw_url(line):
        jsdelivr_pattern = (
            r'https://(?:cdn\.jsdelivr\.net|testingcf\.jsdelivr\.net|fastly\.jsdelivr\.net)'
            r'/gh/([^/]+)/([^@]+)@([^/]+)/(.*)'
        )
        match = re.match(jsdelivr_pattern, line)
        if match:
            user, repo, branch, path = match.groups()
            return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
        for prefix in all_prefixes:
            if line.startswith(prefix):
                if selected_prefix in ("jsdelivr", "testingcf.jsdelivr.net", "fastly.jsdelivr.net") \
                   and "raw.githubusercontent.com" not in line:
                    return line
                return line.replace(prefix, selected_prefix, 1)

        return line

    def convert_to_jsdelivr(raw_url, domain):
        match = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)', raw_url)
        if match:
            user, repo, branch, path = match.groups()
            return f"https://{domain}/gh/{user}/{repo}@{branch}/{path}"
        return raw_url

    def apply_proxy(line):
        original = restore_raw_url(line)
        if selected_prefix in ("jsdelivr", "testingcf.jsdelivr.net", "fastly.jsdelivr.net"):
            if "raw.githubusercontent.com" not in original:
                return original
            if selected_prefix == "jsdelivr":
                domain = "cdn.jsdelivr.net"
            elif selected_prefix == "testingcf.jsdelivr.net":
                domain = "testingcf.jsdelivr.net"
            else:  # fastly
                domain = "fastly.jsdelivr.net"
            return convert_to_jsdelivr(original, domain)
        return re.sub(
            r'^https://raw\.githubusercontent\.com/',
            selected_prefix + 'raw.githubusercontent.com/',
            original
        )

    if isinstance(config, str):
        return apply_proxy(config)

    elif isinstance(config, list):
        return [apply_proxy(line) for line in config]

    else:
        raise TypeError("config 应该是字符串或字符串列表")