import re

def set_gh_proxy(config, selected_index=0):
    proxy_methods = [
        ("gh-proxy.com", "https://gh-proxy.com/"),
        ("cnxiaobai",    "https://github.cnxiaobai.com/"),
        ("ghfast",       "https://ghfast.top/"),
        ("chenc",        "https://github.chenc.dev/"),
        ("jsDelivr",     "https://cdn.jsdelivr.net"),
        ("jsDelivr CF",  "https://testingcf.jsdelivr.net"),
        ("jsDelivr Fastly","https://fastly.jsdelivr.net")
    ]

    if isinstance(selected_index, str):
        selected_index = selected_index.strip()
        if selected_index.isdigit():
            selected_index = int(selected_index) - 1
        else:
            keyword = selected_index.lower()
            found_idx = 0
            for i, (name, url) in enumerate(proxy_methods):
                if keyword in name.lower() or keyword in url.lower():
                    found_idx = i
                    break
            selected_index = found_idx

    if not isinstance(selected_index, int) or selected_index < 0 or selected_index >= len(proxy_methods):
        selected_index = 0

    target_name, target_prefix = proxy_methods[selected_index]

    is_jsdelivr_mode = "jsdelivr" in target_name.lower() or "jsdelivr" in target_prefix.lower()

    def restore_raw_url(line):
        if line.startswith("https://raw.githubusercontent.com/"):
            return line

        jsdelivr_pattern = (
            r'https://(?:cdn|testingcf|fastly)\.jsdelivr\.net'
            r'/gh/([^/]+)/([^@]+)@([^/]+)/(.*)'
        )
        match = re.match(jsdelivr_pattern, line)
        if match:
            user, repo, branch, path = match.groups()
            return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"

        for _, prefix in proxy_methods:
            check_prefix = prefix if prefix.endswith('/') else prefix + '/'
            
            if line.startswith(check_prefix):
                rest = line[len(check_prefix):]
                if rest.startswith("https://raw.githubusercontent.com/"):
                    return rest
                    
                if rest.startswith("raw.githubusercontent.com/"):
                    return "https://" + rest
                    
        return line

    def apply_proxy(line):
        original = restore_raw_url(line)
        
        if "raw.githubusercontent.com" not in original:
            return line

        if is_jsdelivr_mode:
            match = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)', original)
            if match:
                user, repo, branch, path = match.groups()
                clean_prefix = target_prefix.rstrip('/')
                return f"{clean_prefix}/gh/{user}/{repo}@{branch}/{path}"
            return original
        else:
            return target_prefix + original

    if isinstance(config, str):
        return apply_proxy(config)
    elif isinstance(config, list):
        return [apply_proxy(line) for line in config]
    else:
        raise TypeError("config 应该是字符串或字符串列表")