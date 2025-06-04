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






























import re
import pandas as pd

# Precompile regexes
generic_re = re.compile(r"<GenericAttribute\b[^>]*>(.*?)</GenericAttribute>", re.DOTALL)
attr_re    = re.compile(r"<attributeName>\s*(.*?)\s*</attributeName>", re.DOTALL)
desc_re    = re.compile(r"<description>\s*(.*?)\s*</description>", re.DOTALL)
date_re    = re.compile(r"<date>\s*(.*?)\s*</date>", re.DOTALL)

def extract_rsstc_attrs(xml_string):
    if not isinstance(xml_string, str):
        return None
    for block in generic_re.findall(xml_string):
        name_match = attr_re.search(block)
        desc_match = desc_re.search(block)
        date_match = date_re.search(block)

        name_val = name_match.group(1).strip() if name_match else None
        desc_val = desc_match.group(1).strip() if desc_match else None
        date_val = date_match.group(1).strip() if date_match else None

        if (name_val and "RSSTC" in name_val) or (desc_val and desc_val == "Restricted"):
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


















I have two pandas data frames I have created called df_RDM_RSSTC and df_RM_RSSTC. Both of these dataframes have a field called ‘orgStatus’. This field is a string field that contained XML code in <></> style brackets. We will need to use regex to parse this field in order to grab new fields and add them to each record/row of the dataframe. The new fields are called ‘attributeName’, ‘description’, and ‘date’. There are some caveats we need to explore, but before we do that, let me show you the structure and what we will need to parse.
The values can be found in the XML in the group called <orgStatus></orgStatus>, and it is structured like this:
<orgStatus>
<GenericAttribute>
<attributeName>...some data...</attributeName>
<description>...some data...</description>
<date>...some data...</date>
</GenericAttribute>
<GenericAttribute>
...some data...
</GenericAttribute>
<GenericAttribute>
<attributeName>RSSTC</attributeName>
<description>Restricted</description>
<date>date value </date>
</GenericAttribute>
</orgStatus>
As you can see from the structure, the value we are looking is in these brackets <attributeName> </attributeName>, <description> </description>, <date> </date> which are all inside <GenericAttribute></GenericAttribute>.
We will only add the value to each record if and only if the <attributeName> contains the string ‘RSSTC’ or if the description says ‘Restricted’. If it meets this condition, then we can add the description and date values.
If not, we can skip it. If a record does not contain any tags with a match, we can drop that record. All I want at the end of this is an output of attributeNames that match RSSTC or a description that is Restricted.
I want this to output to alteryx like this Alteryx.write(df_example,1) and I need to do this for both dataframes (RDM goes to 1, RM goes to 2). Let me know if you need more information!
