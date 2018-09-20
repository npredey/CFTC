from pathlib import WindowsPath

import quandl
import sys
import os


def validate_input_params(input_params):
    keyset = input_params.keys()
    message = ''
    valid = False
    if 'start_date' in keyset and 'end_date' not in keyset:
        message = "Parameter end_date must be provided along with start_date"
    elif 'end_date' in keyset and 'start_date' not in keyset:
        message = "Parameter start_date must be provided along with end_date"
    else:
        valid = True

    return valid, message


if len(sys.argv) > 1:
    input_name = sys.argv[1]
else:
    input_name = 'quandl_input.txt'

if not os.path.exists(input_name):
    print("Input File [ " + input_name + " ] does not exist. Exiting.")
    exit()
WindowsPath(input_name)
# input_name = "C:\\Users\\npredey\\Downloads\\quandl_input.txt"

ticker_info = {
    "TU": "CFTC/042601_F_ALL_CR",
    "ED": "CFTC/132741_F_ALL_CR",
    "FV": "CFTC/044601_F_ALL_CR",
    "UXY": "CFTC/043607_F_ALL_CR",
    "US": "CFTC/020601_F_L_OLD_CR",
    "WN": "CFTC/020604_F_ALL_CR",
}

input_file = open(input_name, 'r')
input_params = dict()

file_lines = input_file.readlines()
input_file.close()
products = list()
i = 0
for line in file_lines:
    i = i + 1
    if line.startswith('#'):
        continue
    if "start_date" in line:
        input_params["start_date"] = line.split('=')[-1].strip()
    elif "end_date" in line:
        input_params["end_date"] = line.split('=')[-1].strip()
    elif 'output_file' in line:
        input_params['output_file'] = line.split('=')[-1].strip()
    elif 'auth_token' in line:
        input_params['auth_token'] = line.split('=')[-1].strip()
    elif 'products' in line:
        for product in file_lines[i:]:
            if 'end' in product:
                input_params['products'] = products
                break
            else:
                products.append(product.strip().split(','))

valid, message = validate_input_params(input_params)
if not valid:
    print(message)
    print("Exiting")
    exit()

print("Getting data with parameters:")
for key, value in input_params.items():
    print(key, '', value)

# for key, value in ticker_info.items():
output_csv = open(input_params['output_file'], 'w')
header = False
auth_token = input_params['auth_token']
for product in input_params['products']:
    product_uri = product[1]
    product_name = product[0]
    if "start_date" not in input_params.keys():
        rows = quandl.get(product_uri, authtoken=auth_token)
    else:
        rows = quandl.get(product_uri, authtoken=auth_token, start_date=input_params["start_date"],
                          end_date=input_params['end_date'])

        if not header:
            headers = list(rows.columns.values)
            headers.insert(0, "date")
            header = ','.join(headers)
            output_csv.write(header + '\n')
            header = True
        print_product = True
        for row in rows.iterrows():
            if print_product:
                output_csv.write(product_name + '\n')
                print_product = False

            data = row[1]
            print(data)
            date_string = str(row[0].date())
            data_list = data.tolist()
            data_list.insert(0, date_string)
            data = ','.join(str(v) for v in data_list)

            output_csv.write(data + '\n')
output_csv.close()
