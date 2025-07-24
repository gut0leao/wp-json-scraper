import os
import json
import sys

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def tree_categories(categories, parent=0, prefix=""):
    tree = ""
    children = [cat for cat in categories if cat.get("parent", 0) == parent]
    for cat in children:
        tree += f"{prefix}📂 {cat.get('name','')}\n"
        tree += tree_categories(categories, cat.get("id", 0), prefix + "    ")
    return tree

def posts_per_category(posts, categories):
    cat_map = {cat['id']: cat['name'] for cat in categories}
    result = {}
    for post in posts:
        for cat_id in post.get('categories', []):
            cat_name = cat_map.get(cat_id, f"ID:{cat_id}")
            result.setdefault(cat_name, []).append(post.get('title', {}).get('rendered', ''))
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python Report.py <output_dir>")
        sys.exit(1)
    output_dir = sys.argv[1]
    info = load_json(os.path.join(output_dir, "info.json"))
    # Adicione esta verificação:
    if isinstance(info, list) and len(info) > 0:
        info = info[0]
    categories = load_json(os.path.join(output_dir, "categories.json")) or []
    tags = load_json(os.path.join(output_dir, "tags.json")) or []
    posts = load_json(os.path.join(output_dir, "posts.json")) or []
    pages = load_json(os.path.join(output_dir, "pages.json")) or []
    media = load_json(os.path.join(output_dir, "media.json")) or []
    users = load_json(os.path.join(output_dir, "users.json")) or []

    report_lines = []
    report_lines.append("=========================")
    report_lines.append("REPORT FROM EXTRATED DATA")
    report_lines.append("=========================\n")

    # Target info
    report_lines.append("Target info (info.json):")
    url = info.get("url", "N/A") if info else "N/A"
    name = info.get("name", "N/A") if info else "N/A"
    report_lines.append(f"🌐 url: {url}")
    report_lines.append(f"🏷️ name: {name}\n")

    # Categories
    report_lines.append(f"📂 Number of Categories: {len(categories)}")
    report_lines.append(f"🏷️ Number of Tags: {len(tags)}")
    report_lines.append(f"📝 Number of posts (total): {len(posts)}")

    # Posts per category
    ppc = posts_per_category(posts, categories)
    report_lines.append("🗂️ Number of posts per category:")
    for cat, plist in ppc.items():
        report_lines.append(f"  - {cat}: {len(plist)}")
    report_lines.append(f"📄 Number of pages: {len(pages)}\n")

    # Categories tree
    report_lines.append("Categories:")
    report_lines.append(tree_categories(categories))

    # Tags
    report_lines.append("Tags:")
    report_lines.append("  " + ", ".join([f"🏷️ {tag.get('name','')}" for tag in tags]) + "\n")

    # Posts por categoria
    report_lines.append("Posts por categoria:")
    for cat, plist in ppc.items():
        report_lines.append(f"  📂 {cat}:")
        for post_title in plist:
            report_lines.append(f"    - 📝 {post_title}")
    report_lines.append("")

    # Pages
    report_lines.append("Pages:")
    for page in pages:
        title = page.get('title', {}).get('rendered', page.get('title', ''))
        report_lines.append(f"  📄 {title}")
    report_lines.append("")

    # Media
    report_lines.append("Media:")
    for m in media:
        url = m.get('source_url', m.get('guid', {}).get('rendered', ''))
        name = m.get('title', {}).get('rendered', m.get('title', ''))
        report_lines.append(f"  🖼️ {name} ({url})")
    report_lines.append("")

    # Users
    report_lines.append("Users list (users.json):")
    # Cria um mapa de posts por usuário
    user_post_count = {}
    for post in posts:
        author_id = post.get('author')
        user_post_count[author_id] = user_post_count.get(author_id, 0) + 1

    # Cria lista de usuários com contagem de posts
    users_with_count = []
    for user in users:
        user_id = user.get('id')
        name = user.get('name', user.get('username', ''))
        post_count = user_post_count.get(user_id, 0)
        users_with_count.append((name, post_count))

    # Ordena pela quantidade de posts (decrescente)
    users_with_count.sort(key=lambda x: x[1], reverse=True)

    for name, post_count in users_with_count:
        report_lines.append(f"  👤 {name} [{post_count} posts]")
    report_lines.append("")

    # Write report.txt
    with open(os.path.join(output_dir, "report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

if __name__ == "__main__":
    main()