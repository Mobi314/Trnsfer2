import re
import pandas as pd

# ---------------------------------------
# 1) Define a helper that parses one XML string
# ---------------------------------------
def extract_rsstc_attrs(xml_string):
    """
    Given the contents of the <orgStatus>…</orgStatus> field (as a single string),
    find the first <GenericAttribute> block where either:
      - <attributeName> contains "RSSTC"
      - OR <description> == "Restricted"
    Return a dict with keys "attributeName", "description", "date",
    or return None if no matching block exists.
    """
    if not isinstance(xml_string, str):
        return None

    # Look for each <GenericAttribute>…</GenericAttribute> block
    #    Note: DOTALL so that newlines inside tags are captured.
    for block in re.findall(r"<GenericAttribute>(.*?)</GenericAttribute>", xml_string, re.DOTALL):
        # Within that block, try to pull out each sub‐tag
        name_match = re.search(r"<attributeName>\s*(.*?)\s*</attributeName>", block, re.DOTALL)
        desc_match = re.search(r"<description>\s*(.*?)\s*</description>", block, re.DOTALL)
        date_match = re.search(r"<date>\s*(.*?)\s*</date>", block, re.DOTALL)

        name_val = name_match.group(1) if name_match else None
        desc_val = desc_match.group(1) if desc_match else None
        date_val = date_match.group(1) if date_match else None

        # Keep if attributeName contains "RSSTC" or description is exactly "Restricted"
        if (name_val and "RSSTC" in name_val) or (desc_val and desc_val.strip() == "Restricted"):
            return {
                "attributeName": name_val,
                "description":   desc_val,
                "date":          date_val
            }

    # If we get here, no matching block was found
    return None


# ---------------------------------------
# 2) Apply that helper to each DataFrame
# ---------------------------------------
def filter_and_expand(df):
    """
    Given a DataFrame with a column 'orgStatus' (string),
    add three new columns ['attributeName','description','date'],
    keep only rows where extract_rsstc_attrs(...) is not None.
    """
    # 2a) Run extract_rsstc_attrs(...) on every row
    parsed = df["orgStatus"].apply(extract_rsstc_attrs)

    # 2b) Turn the list of dicts/None into a DataFrame (each row → a dict or None)
    parsed_df = pd.DataFrame(parsed.tolist())

    # 2c) Concat the new columns back onto the original
    result = pd.concat([df.reset_index(drop=True), parsed_df], axis=1)

    # 2d) Drop all rows where parsed_df is all null (i.e. no matching <GenericAttribute>)
    result = result.dropna(subset=["attributeName", "description", "date"], how="all")

    return result


# ---------------------------------------
# 3) Run this for each of your two DataFrames,
#    then write back to Alteryx
# ---------------------------------------
# (Assuming df_RDM_RSSTC and df_RM_RSSTC already exist)

df_RDM_filtered = filter_and_expand(df_RDM_RSSTC)
df_RM_filtered  = filter_and_expand(df_RM_RSSTC)

# Finally, send each back to Alteryx with the specified output anchor:
Alteryx.write(df_RDM_filtered, 1)
Alteryx.write(df_RM_filtered, 2)
