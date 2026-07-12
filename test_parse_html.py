import csv 
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


# ==========================
# FUNCTIONS
# ==========================

def fetch_page(url):
    response = requests.get(url, timeout=20)
    return BeautifulSoup(response.text, "html.parser")

def get_policy_page(link):
    return fetch_page(link)

def extract_policy_text(policy_soup):
    main_title = policy_soup.find("div", class_="eli-main-title")

    if main_title is None:
        return ""

    content = main_title.find_all("p", class_="oj-doc-ti")

    policy_text = ""

    for paragraph in content:
        policy_text += paragraph.text.strip() + "\n"

    return policy_text

def extract_metadata(policy_text, link):
    return {
        "policy_type": policy_text.split()[0],
        "policy_year": policy_text.split()[2].split("/")[0],
        "policy_id": link.split("CELEX:")[1].split("&")[0],
        "word_count": len(policy_text.split()),
        "policy_summary": policy_text.split("\n")[2],
        "policy_length": len(policy_text),
    }

def generate_tags(policy_summary):
    policy_summary_lower = policy_summary.lower()

    tags = []

    if "climate" in policy_summary_lower:
        tags.append("Climate")

    if "energy" in policy_summary_lower:
        tags.append("Energy")

    if "transport" in policy_summary_lower:
        tags.append("Transport")

    if "rail" in policy_summary_lower:
        tags.append("Transport")

    if "environment" in policy_summary_lower:
        tags.append("Environment")

    if "digital" in policy_summary_lower:
        tags.append("Digital")

    if "technology" in policy_summary_lower:
        tags.append("Technology")

    if "youth" in policy_summary_lower:
        tags.append("Youth")

    if "skills" in policy_summary_lower:
        tags.append("Skills")

    if "agriculture" in policy_summary_lower:
        tags.append("Agriculture")

    if "green" in policy_summary_lower:
        tags.append("Green Deal")

    return tags

def extract_status(result):
    status = result.find("div", class_="DocStatus")
    return status.text.strip()

def get_source():
    return "EUR-Lex"

def export_json(documents):
    with open("documents.json", "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=4, ensure_ascii=False)


def export_csv(documents):
    with open("documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=documents[0].keys())
        writer.writeheader()
        writer.writerows(documents)

def load_dataframe():
    return pd.read_csv("documents.csv")


def scrape_policies():

    url = "https://eur-lex.europa.eu/search.html?scope=EURLEX&text=European+Green+Deal&lang=en&type=quick"

    soup = fetch_page(url)

    results = soup.find_all("div", class_="SearchResult")

    #print(response.status_code)
    #print(len(results))

    documents = []
    for result in results:
        a = result.find("h2").find("a")

        title = a.text.strip()
        link = a["href"]
        link = "https://eur-lex.europa.eu/" + link.replace("./", "")
        policy_soup = get_policy_page(link)

        policy_text = extract_policy_text(policy_soup)
        metadata = extract_metadata(policy_text, link)
        

        if not policy_text:
            continue
            
        status = extract_status(result)
        
        tags = generate_tags(metadata["policy_summary"])
        
        source = get_source()
        documents.append({
        "title": title,
        "link": link,
        "status": status,
        "policy_type": metadata["policy_type"],
        "policy_year": metadata["policy_year"],
        "policy_id": metadata["policy_id"],
        "policy_summary": metadata["policy_summary"],
        "source": source,
        "tags": tags,
        "policy_length": metadata["policy_length"],
        "word_count": metadata["word_count"],
        })

    documents.sort(key=lambda x: x["policy_year"], reverse=True)

    return documents
    
def main():
    documents = scrape_policies()
    export_json(documents)
    export_csv(documents)

    df = load_dataframe()

    print(df.head())
    print(df.info())
    print(df.describe())

    df["policy_type"].value_counts().plot(kind="bar")

    plt.title("Policy Type Distribution")
    plt.xlabel("Policy Type")
    plt.ylabel("Number of Policies")
    plt.savefig("outputs/plots/policy_type_distribution.png", dpi=300, bbox_inches="tight")
    plt.show()
    print(df["policy_year"].value_counts())
    df["policy_year"].value_counts().sort_index().plot(kind="bar")

    plt.title("Policies by Year")
    plt.xlabel("Publication Year")
    plt.ylabel("Number of Policies")

    plt.savefig("outputs/plots/policies_by_year.png", dpi=300, bbox_inches="tight")

    plt.show()
    print(df.groupby("policy_year")["policy_type"].value_counts())
    pivot_table = pd.crosstab(df["policy_year"], df["policy_type"])

    print(pivot_table)
    pivot_table.plot(kind="bar")

    plt.title("Policy Types by Year")
    plt.xlabel("Publication Year")
    plt.ylabel("Number of Policies")

    plt.savefig("outputs/plots/policy_types_by_year.png", dpi=300, bbox_inches="tight")

    plt.show()
    policy_summary = df.groupby("policy_type").agg({
        "word_count": "mean",
        "policy_length": "mean"
    })

    print(policy_summary)
    print(df.columns)
    print(df.sort_values("word_count", ascending=False)[
        ["title", "word_count"]
    ].head())
    print(
        df.sort_values("word_count")[
            ["title", "word_count"]
        ].head()
    )
    top_3_policies = df.sort_values(
        "word_count",
        ascending=False
    ).head(3)

    print(top_3_policies[["title", "word_count"]])
    top_3_policies.to_csv(
        "outputs/top_3_longest_policies.csv",
        index=False
    )
    df["reading_time_minutes"] = (df["word_count"] / 200).round(2)

    print(
        df[
            ["title", "word_count", "reading_time_minutes"]
        ].head()
    )

if __name__ == "__main__":
    main()

    