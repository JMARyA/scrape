from selenium.webdriver.common.by import By
from ..val import printinfo, get_webdriver


def aur_package(url: str, conf) -> dict:
    b = get_webdriver(conf)
    printinfo(f"Scraping '{url}'")
    b.get(url)

    head = b.find_element(By.XPATH, '//*[@id="pkgdetails"]/h2').text[17:]
    (name, version) = head.split(" ")

    pkg_info = b.find_element(By.XPATH, '//*[@id="pkginfo"]')

    info = {"name": name, "version": version}

    for row in pkg_info.find_elements(By.TAG_NAME, "tr"):
        match row.find_element(By.TAG_NAME, "th").text:
            case "Git Clone URL:":
                clone_url = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                info["clone"] = clone_url
            case "Description:":
                desc = row.find_element(By.TAG_NAME, "td").text
                info["description"] = desc
            case "Upstream URL:":
                upstream_url = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                info["upstream"] = upstream_url
            case "Keywords:":
                keywords_items = row.find_elements(By.TAG_NAME, "a")
                keywords = []
                for keyword in keywords_items:
                    keywords.append(keyword.text)
                info["keywords"] = keywords
            case "Licenses:":
                license = row.find_element(By.TAG_NAME, "td").text
                info["license"] = license
            case "Submitter:":
                submitter = row.find_element(By.TAG_NAME, "td").text
                info["submitter"] = submitter
            case "Maintainer:":
                maintainer = row.find_element(By.TAG_NAME, "td").text
                info["maintainer"] = maintainer
            case "Last Packager:":
                last_packager = row.find_element(By.TAG_NAME, "td").text
                info["last_packager"] = last_packager
            case "Votes:":
                votes = row.find_element(By.TAG_NAME, "td").text
                info["votes"] = int(votes)
            case "Popularity:":
                popularity = row.find_element(By.TAG_NAME, "td").text
                info["popularity"] = popularity
            case "First Submitted:":
                first_submitted = row.find_element(By.TAG_NAME, "td").text
                info["first_submitted"] = first_submitted
            case "Last Updated:":
                last_updated = row.find_element(By.TAG_NAME, "td").text
                info["last_updated"] = last_updated

    dependencies = []
    dependency_items = b.find_element(By.XPATH, '//*[@id="pkgdepslist"]')
    deps = dependency_items.find_elements(By.TAG_NAME, "li")
    if "Show " in deps[-1].text:
        b.get(deps[-1].find_element(By.XPATH, "./a").get_attribute("href"))
        dependency_items = b.find_element(By.XPATH, '//*[@id="pkgdepslist"]')
        deps = dependency_items.find_elements(By.TAG_NAME, "li")

    for dep in deps:
        dep_name = dep.find_element(By.TAG_NAME, "a").text
        dep_info = dep.find_elements(By.TAG_NAME, "em")[-1].text
        dependencies.append({"name": dep_name, "info": dep_info})

    info["dependencies"] = dependencies

    required_by = []

    required_by_items = b.find_element(By.XPATH, '//*[@id="pkgreqslist"]')
    reqs = required_by_items.find_elements(By.TAG_NAME, "li")
    if "Show " in reqs[-1].text:
        b.get(reqs[-1].find_element(By.XPATH, "./a").get_attribute("href"))
        required_by_items = b.find_element(By.XPATH, '//*[@id="pkgreqslist"]')
        reqs = required_by_items.find_elements(By.TAG_NAME, "li")

    for req in reqs:
        req_name = req.find_element(By.TAG_NAME, "a").text
        req_info = req.find_elements(By.TAG_NAME, "em")[-1].text
        required_by.append(
            {
                "name": req_name,
                "optional": True if req_info == "(optional)" else False,
            }
        )

    info["required_by"] = required_by

    sources = []
    for source in b.find_element(By.XPATH, '//*[@id="pkgsrcslist"]').find_elements(
        By.TAG_NAME, "li"
    ):
        sources.append(source.find_element(By.TAG_NAME, "a").get_attribute("href"))

    info["sources"] = sources

    b.quit()
    return info
