import re
from urllib.parse import parse_qs, urlparse, urlencode, urlunparse, quote, unquote

def set_gh_proxy(config, gh="1"):
    proxy_methods = [
        ("gh-proxy", "https://gh-proxy.com/"),
        ("sageer", "https://gh.sageer.me/"),
        ("ghproxy", "https://ghproxy.com/"),
        ("mirror", "https://mirror.ghproxy.com/"),
        ("cdn", "https://cdn.jsdelivr.net"),
        ("testingcf", "https://testingcf.jsdelivr.net"),
        ("fastly", "https://fastly.jsdelivr.net")
    ]

    if gh.isdigit():
        selected_index = int(gh) - 1
        if not (0 <= selected_index < len(proxy_methods)):
            raise ValueError(f"gh 数字索引超出范围: {gh}")
        selected_name, selected_prefix = proxy_methods[selected_index]
    else:
        for name, prefix in proxy_methods:
            if name == gh:
                selected_name, selected_prefix = name, prefix
                break
        else:
            raise ValueError(f"未知 GitHub 加速名称: {gh}")

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
                if selected_prefix in ("https://cdn.jsdelivr.net", "https://testingcf.jsdelivr.net", "https://fastly.jsdelivr.net") \
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

        if selected_prefix in ("https://cdn.jsdelivr.net", "https://testingcf.jsdelivr.net", "https://fastly.jsdelivr.net"):
            if "raw.githubusercontent.com" not in original:
                return original

            if selected_prefix == "https://cdn.jsdelivr.net":
                domain = "cdn.jsdelivr.net"
            elif selected_prefix == "https://testingcf.jsdelivr.net":
                domain = "testingcf.jsdelivr.net"
            else:
                domain = "fastly.jsdelivr.net"
            return convert_to_jsdelivr(original, domain)
        return re.sub(
            r'^https://raw\.githubusercontent\.com/',
            selected_prefix + 'raw.githubusercontent.com/',
            original
        )

    def process_url(full_url):
        parsed = urlparse(full_url)
        qs = parse_qs(parsed.query)

        if "file" in qs:
            original_file = unquote(qs["file"][0])
            if original_file.startswith("https:/") and not original_file.startswith("https://"):
                original_file = original_file.replace("https:/", "https://", 1)
            converted_file = apply_proxy(original_file)
            qs["file"] = [quote(converted_file, safe=":/@")]
            new_query = urlencode(qs, doseq=True)
            return urlunparse(parsed._replace(query=new_query))
        else:
            return apply_proxy(full_url)

    if isinstance(config, str):
        return process_url(config)
    elif isinstance(config, list):
        return [process_url(url) for url in config]
    else:
        raise TypeError("config 应该是字符串或字符串列表")