def extract_fields(xml_block):
    def get_value(tag):
        match = re.search(f'<{tag}>(.*?)</{tag}>', xml_block, re.DOTALL)
        return match.group(1).strip() if match else ''

    return {
        'stbkCode': get_value('stbkCode'),
        'spLevel': get_value('spLevel'),
        'gbsId': get_value('gbsId'),
        'shortName': get_value('shortName'),
        'longName': get_value('longName'),
        'riskManagedRegion': get_value('riskManagedRegion')
    }

parsed_rows = []

for _, row in df_GBS.iterrows():
    xml_data = row.get('rdmLegacyData', '')
    base_row = row.to_dict()

    if not isinstance(xml_data, str) or '<GBSRdmLegacyData>' not in xml_data:
        # No XML or irrelevant content: retain original row with empty fields
        base_row.update({
            'stbkCode': '',
            'spLevel': '',
            'gbsId': '',
            'shortName': '',
            'longName': '',
            'riskManagedRegion': ''
        })
        parsed_rows.append(base_row)
        continue

    # Find all <GBSRdmLegacyData>...</GBSRdmLegacyData> blocks
    blocks = re.findall(r'<GBSRdmLegacyData>(.*?)</\s*GBSRdmLegacyData\s*>', xml_data, re.DOTALL)

    added = False
    for block in blocks:
        sp_level_match = re.search(r'<spLevel>(.*?)</spLevel>', block, re.DOTALL)
        if sp_level_match and sp_level_match.group(1).strip() == 'SP1':
            extracted = extract_fields(block)
            new_row = base_row.copy()
            new_row.update(extracted)
            parsed_rows.append(new_row)
            added = True

    # If no SP1 match found, include the original row with empty fields
    if not added:
        base_row.update({
            'stbkCode': '',
            'spLevel': '',
            'gbsId': '',
            'shortName': '',
            'longName': '',
            'riskManagedRegion': ''
        })
        parsed_rows.append(base_row)

# Create the parsed DataFrame
df_GBS_Parsed = pd.DataFrame(parsed_rows)

# Output to Alteryx
Alteryx.write(df_GBS_Parsed, 1)
