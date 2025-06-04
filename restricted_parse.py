import re
import pandas as pd

def extract_rsstc_attrs(xml_string):
    if not isinstance(xml_string, str):
        return None
    for block in re.findall(r"<GenericAttribute>(.*?)</GenericAttribute>", xml_string, re.DOTALL):
        name_match = re.search(r"<attributeName>\s*(.*?)\s*</attributeName>", block, re.DOTALL)
        desc_match = re.search(r"<description>\s*(.*?)\s*</description>", block, re.DOTALL)
        date_match = re.search(r"<date>\s*(.*?)\s*</date>", block, re.DOTALL)

        name_val = name_match.group(1) if name_match else None
        desc_val = desc_match.group(1) if desc_match else None
        date_val = date_match.group(1) if date_match else None

        if (name_val and "RSSTC" in name_val) or (desc_val and desc_val.strip() == "Restricted"):
            return {"attributeName": name_val, "description": desc_val, "date": date_val}
    return None

def filter_and_expand(df):
    parsed = df["orgStatus"].apply(extract_rsstc_attrs)
    df = df.copy()
    df["attributeName"] = None
    df["description"]   = None
    df["date"]          = None

    mask = parsed.notna()
    df.loc[mask, "attributeName"] = parsed[mask].apply(lambda d: d["attributeName"])
    df.loc[mask, "description"]   = parsed[mask].apply(lambda d: d["description"])
    df.loc[mask, "date"]          = parsed[mask].apply(lambda d: d["date"])

    result = df.dropna(subset=["attributeName", "description", "date"], how="all")
    return result

df_RDM_filtered = filter_and_expand(df_RDM_RSSTC)
df_RM_filtered  = filter_and_expand(df_RM_RSSTC)

Alteryx.write(df_RDM_filtered, 1)
Alteryx.write(df_RM_filtered, 2)






























def extract_rsstc_attrs(xml_string):
    if not isinstance(xml_string, str):
        return None
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        return None

    for ga in root.findall(".//GenericAttribute"):
        name_val = ga.findtext("attributeName")
        desc_val = ga.findtext("description")
        date_val = ga.findtext("date")

        if (name_val and "RSSTC" in name_val) or (desc_val and desc_val.strip() == "Restricted"):
            return {"attributeName": name_val, "description": desc_val, "date": date_val}
    return None

def filter_and_expand(df):
    parsed = df["orgStatus"].apply(extract_rsstc_attrs)

    df = df.copy()
    df["attributeName"] = None
    df["description"]   = None
    df["date"]          = None

    mask = parsed.notna()
    df.loc[mask, "attributeName"] = parsed[mask].apply(lambda d: d["attributeName"])
    df.loc[mask, "description"]   = parsed[mask].apply(lambda d: d["description"])
    df.loc[mask, "date"]          = parsed[mask].apply(lambda d: d["date"])

    return df.dropna(subset=["attributeName", "description", "date"], how="all")

df_RDM_filtered = filter_and_expand(df_RDM_RSSTC)
df_RM_filtered  = filter_and_expand(df_RM_RSSTC)

Alteryx.write(df_RDM_filtered, 1)
Alteryx.write(df_RM_filtered, 2)

