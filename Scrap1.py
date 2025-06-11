import json

from bs4 import BeautifulSoup
import requests


def fetch_articles(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(e)
        return []

    main_tag = soup.find("main")
    archive_div = main_tag.select_one("div.archive-list")

    articles = archive_div.find_all("article")
    return articles

def scrape_article_detail(article_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

    except requests.exceptions.RequestException as e:
        print(e)
        return []
    return soup


# Appel
Natricle = 1
stockage = {}
for pages in range(0, 1):
    compil_url = "https://www.blogdumoderateur.com/web/page/" + str(pages) + "/"
    print("url ciblé :", compil_url)
    articles = fetch_articles(compil_url)

    for article in articles:
        stockage[Natricle] = {}

        h3 = article.find("h3")
        img = article.find("img")
        category = article.select_one("span.favtag")
        resume = article.select_one("div.entry-excerpt")
        link_tag = article.find("a")

        # titre de l'aricle
        if h3:
            print("Titre Article :", h3.text.strip())
            stockage[Natricle]["Titre"] = h3.text.strip()
        # thumbnail de l'article
        if img:
            img_src = img.get("data-lazy-src") or img.get("src")
            print("Image Article :", img_src)
            stockage[Natricle]["Image"] = img_src
        # categorie de l'article
        if category:
            print("Category :", category.text.strip())
            stockage[Natricle]["Category"] = category.text.strip()
        # resumé des article
        if resume:
            print("Resume :", resume.text.strip())
            stockage[Natricle]["Resumé"] = resume.text.strip()

        if link_tag and link_tag.get("href"):
            url_article = link_tag["href"]
            print("Lien :", url_article)
            stockage[Natricle]["Link"] = url_article
            # debut gestion des article interne
            details = scrape_article_detail(url_article)

            auteur = details.select_one("span.byline a")
            date = details.select_one("time.entry-date")
            blocks = details.select("article p, article h2, article h3, article li")
            contenu_clean = ""
            images = []
            figures = details.select("article figure")
            tags_section = details.select_one("ul.tags-list")
            sous_categories = []

            # Sous categorie (cauchemard, je doute de son fonctionnement complet)
            if tags_section:
                tags = tags_section.select("a.post-tags")
                for tag in tags:
                    nom = tag.get_text(strip=True)
                    href = tag.get("href")
                    if nom:
                        sous_categories.append({
                            "nom": nom,
                            "url": href
                        })

            if sous_categories:
                stockage[Natricle]["Sous-catégories"] = sous_categories
                print("Sous-catégories :", sous_categories)

            # auteur + date
            if auteur:
                nom_auteur = auteur.text.strip()
                stockage[Natricle]["Auteur"] = nom_auteur
                print("Auteur :", nom_auteur)
            if date:
                date_publi = date.text.strip()
                stockage[Natricle]["Date de publication"] = date_publi
                print("Publié le :", date_publi)
            # contenu artcile
            for block in blocks:
                text = block.get_text(strip=True)
                if text:
                    contenu_clean += text + "\n"

            if contenu_clean:
                print("Contenu nettoyé :")
                print(contenu_clean)
                stockage[Natricle]["Contenu"] = contenu_clean.strip()

            #dico img
            for fig in figures:
                img_tag = fig.find("img")
                caption_tag = fig.find("figcaption")

                if img_tag:
                    img_src = img_tag.get("data-lazy-src") or img_tag.get("src")
                    caption = caption_tag.get_text(strip=True) if caption_tag else ""

                    images.append({
                        "src": img_src,
                        "caption": caption
                    })
            if images:
                stockage[Natricle]["Dictionnaire_Images"] = images

        Natricle += 1

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(stockage, f, ensure_ascii=False, indent=4)
