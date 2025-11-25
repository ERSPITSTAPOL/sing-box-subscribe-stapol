import re

def set_gh_proxy(config, selected_index=0):
    proxy_methods = {
        1: ("gh-proxy.com", "https://gh-proxy.com/"),
        2: ("cnxiaobai",    "https://github.cnxiaobai.com/"),
        3: ("ghfast",       "https://ghfast.top/"),
        4: ("chenc",        "https://github.chenc.dev/"),
        5: ("jsDelivr",     "https://cdn.jsdelivr.net"),
        6: ("jsDelivr CF",  "https://testingcf.jsdelivr.net"),
        7: ("jsDelivr Fastly","https://fastly.jsdelivr.net")
    }
    MAX_INDEX = len(proxy_methods)

    if isinstance(selected_index, str):
        selected_index = selected_index.strip()
        
        if selected_index.isdigit():
            selected_index = int(selected_index) 
        else:
            keyword = selected_index.lower()
            found_key = 1
            for key, (name, url) in proxy_methods.items():
                if keyword in name.lower() or keyword in url.lower():
                    found_key = key
                    break
            selected_index = found_key
    
    if selected_index == 0:
        selected_index = 1
    if not isinstance(selected_index, int) or selected_index < 1 or selected_index > MAX_INDEX:
        selected_index = 1
    
    target_name, target_prefix = proxy_methods[selected_index]
    is_jsdelivr_mode = "jsdelivr" in target_name.lower() or "jsdelivr" in target_prefix.lower()

    def restore_raw_url(line):
        line = line.strip() 
        raw_prefix = "https://raw.githubusercontent.com/"
        
        if line.startswith(raw_prefix):
            return line

        jsdelivr_pattern = (
            r'(?:https://(?:cdn|testingcf|fastly)\.jsdelivr\.net)'
            r'/gh/([^/]+)/([^@]+)@([^/]+)/(.*)'
        )
        raw_sub = r'https://raw.githubusercontent.com/\1/\2/\3/\4'
        new_line, count = re.subn(jsdelivr_pattern, raw_sub, line)
        
        if count > 0:
            return new_line
        
        for _, prefix in proxy_methods.values():
            check_prefix = prefix if prefix.endswith('/') else prefix + '/'
            
            if line.startswith(check_prefix):
                rest = line[len(check_prefix):]
                if rest.startswith(raw_prefix) or rest.startswith(raw_prefix.replace("https://", "")):
                    return rest if rest.startswith("https://") else "https://" + rest
        
        raw_index = line.find(raw_prefix)
        if raw_index > 0:
            return line[raw_index:]
        
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