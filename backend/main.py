import json
import re
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from extraction_service import ContractDataExtractionService
from fedex_extraction_service import FedexContractDataExtractionService
from api_rates import APIRates  # Import APIRates class from api_rates.py
import difflib
from dotenv import load_dotenv
from api_rates import Address, Parcel  # Adjust the import path based on your project structure

load_dotenv()  # Load environment variables from .env file

# FastAPI setup
app = FastAPI()

# Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    # Allow all domains (use specific domains in production)
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


class DiscountInput(BaseModel):
    weekly_price: float
    start_address: Address
    destination_address: Address 
    parcel: Parcel
    tables_json: str
    contract_type: str


@app.get("/")
async def read_root():
    return JSONResponse(content={"success": True, "message": "Server is running"})


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    extracted_data = FedexContractDataExtractionService.extract(file)
    # details = extracted_data["details"]
    tables = extracted_data["tables"]
    # source_address = extracted_data["address"]
    # contract_type = extracted_data["contract_type"]
    return JSONResponse(content={"success": True, "message": "Extracted data", "data": {
        # "details": details,
        "tables": tables,
        # "source_address": source_address,
        # "contract_type": contract_type
    }})


def find_best_match(service_name, service_list):
    """
    Finds the closest matching service name from the available list.
    Handles differences in encoding, extra words, and minor variations.
    """
    cleaned_service_name = re.sub(r"[^a-zA-Z0-9 ]", "", service_name).lower().strip()
    cleaned_service_list = [
        re.sub(r"[^a-zA-Z0-9 ]", "", s).lower().strip().replace("  ", " ")
        for s in service_list
    ]

    matched_services = []
    for service in cleaned_service_list:
        if cleaned_service_name in service:
            matched_services.append(service_list[cleaned_service_list.index(service)])
    # print("service name",service_name, "matched service",matched_services)
    if matched_services:
        return matched_services
        

    best_match = difflib.get_close_matches(
        cleaned_service_name, cleaned_service_list, n=1, cutoff=0.9)
    abc= service_list[cleaned_service_list.index(best_match[0])] if best_match else None
    # print("service name",service_name, "abc service",abc)
    return abc


def parse_band(band):
    """Parses the incentive band to get min and max range as floats."""
    if not band:
        return None, None
    band = band.replace(",", "").replace("\n", " ").replace("  ", " ")  # Remove commas and extra spaces
    if "and up" in band:
        try:
            return float(band.split(" ")[0]), float("inf")
        except ValueError:
            pass
    parts = band.split(" - ") if " - " in band else band.split("-")
    if len(parts) == 2:
        try:
            return float(parts[0]), float(parts[1])
        except ValueError:
            pass
    elif "and up" in band:
        try:
            return float(band.split(" ")[0]), float("inf")
        except ValueError:
            pass
    return None, None


def get_portfolio_tier_incentive(table_data, weekly_price: float):
    applicable_services = []
    # Loop through each table in the extracted JSON data.
    for tier in table_data.get("tables", []):
        if tier.get("table_type") == "portfolio_tier_incentives":
            for entry in tier.get("data", []):
                band = entry.get("band")
                if not band:
                    continue
                min_band, max_band = parse_band(band)
                # print("min band",min_band,"max band",max_band)
                if min_band is None or max_band is None:
                    continue
                if min_band <= weekly_price <= max_band:
                    print("min band",min_band, "max band",max_band)
                    incentive_value = entry.get("incentive")
                    if not incentive_value:
                        continue
                    try:
                        incentive_float = float(incentive_value.replace("%", "").replace("- ", ""))
                    except ValueError:
                        continue
                    applicable_services.append({
                        "service": entry.get("service", ""),
                        "incentive": incentive_float
                    })
    return applicable_services


def get_incentive_off_executive(table_data, service_name: str, weekly_price: float,weight:float):
    incentives = []
    for tier in table_data.get("tables", []):
        if tier.get("table_type") == "weight_zone_incentive" and tier.get("name") and (
            service_name in tier["name"] or find_best_match(service_name, [tier["name"]])
        ):
            for row in tier.get("data", []):
                min_wt, max_wt=parse_band(row.get("weight"))
                incentive_value = row.get("incentive")
                if not incentive_value:
                    continue
                if min_wt is not None and max_wt is not None:
                    if min_wt <= weight <= max_wt:
                        try:
                            incentive_float = abs(float(incentive_value.replace("%", "").replace("- ", "")))
                        except ValueError:
                            continue
                        incentives.append(incentive_float)

        if tier.get("table_type") == "zone_bands_incentive" and tier.get("name") and (
            service_name in tier["name"] or find_best_match(service_name, [tier["name"]])
        ):
            for row in tier.get("data", []):
                incentive_value = row.get("incentive")
                if not incentive_value:
                    continue
                min_band, max_band = parse_band(row.get("band", ""))
                if min_band is not None and max_band is not None:
                    if min_band <= weekly_price <= max_band:
                        try:
                            incentive_float = abs(float(incentive_value.replace("%", "").replace("- ", "")))
                        except ValueError:
                            continue
                        incentives.append(incentive_float)

        if tier.get("table_type") == "zone_incentive" and tier.get("name") and (
            service_name in tier["name"] or find_best_match(service_name, [tier["name"]])
        ):
            for row in tier.get("data", []):
                incentive_value = row.get("incentive")
                if not incentive_value:
                    continue
                try:
                    incentive_float = abs(float(incentive_value.replace("%", "").replace("- ", "")))
                except ValueError:
                    continue
                incentives.append(incentive_float)

        if tier.get("table_type") == "service_incentives":
            for row in tier.get("data", []):
                incentive_value = row.get("incentive")
                if not incentive_value:
                    continue
                service_row = row.get("service", "")
                if service_name in service_row or find_best_match(service_name, [service_row]):
                    try:
                        incentive_float = abs(float(incentive_value.replace("%", "").replace("- ", "")))
                    except ValueError:
                        continue
                    incentives.append(incentive_float)
    return sum(incentives) / len(incentives) if incentives else 0


def get_maximum_possible_discount(table_data, service_name: str):
    incentives = []
    for tier in table_data.get("tables", []):
        if tier.get("table_type") == "zone_incentive_min_charge" and tier.get("name") and (
            service_name in tier["name"] or find_best_match(service_name, [tier["name"]])
        ):
            for row in tier.get("data", []):
                incentive_value = row.get("incentive")
                if not incentive_value:
                    continue
                try:
                    incentive_float = abs(float(incentive_value.replace("%", "").replace("- ", "")))
                    # print("service name",tier["name"],"incentive float",incentive_float)
                except ValueError:
                    continue
                incentives.append(incentive_float)
        if tier.get("table_type") == "service_min_per_zone_base_rate_adjustment":
            for row in tier.get("data", []):
                incentive_value = row.get("adjustment")
                if not incentive_value:
                    continue
                service_row = row.get("service", "")
                if service_name in service_row or find_best_match(service_name, [service_row]):
                    try:
                        incentive_float = abs(float(incentive_value.replace("%", "").replace("- ", "")))
                        print("service name",service_name,"incentive float 2",incentive_float)
                    except ValueError:
                        continue
                    incentives.append(incentive_float)
    maximum_possible_discount = max(incentives) if incentives else 0
    return (100 - maximum_possible_discount) if maximum_possible_discount else 100


@app.post("/calculate_discount")
async def calculate_discount(input_data: DiscountInput):
    weekly_price = input_data.weekly_price
    start_address = input_data.start_address
    destination_address = input_data.destination_address
    parcel = input_data.parcel
    tables_json = input_data.tables_json
    contract_type = input_data.contract_type
    table_data = json.loads(tables_json)

    print(f"Processing discount calculation:")
    print(f"Weekly Price: ${weekly_price}")
    print(f"Start Address: {start_address.street}, {start_address.city}, {start_address.state} {start_address.zip}, {start_address.country}")
    print(f"Destination Address: {destination_address.street}, {destination_address.city}, {destination_address.state} {destination_address.zip}, {destination_address.country}")
    print(f"Parcel: {parcel.length}x{parcel.width}x{parcel.height} {parcel.weight} lbs")
    print(f"Contract Type: {contract_type}")
    print(f"Number of tables in input: {len(table_data.get('tables', []))}")
    
    if not destination_address.zip or not start_address.zip:
        return JSONResponse(content={"success": False, "message": "Invalid Address"}, status_code=400)

    # Step 1: Get Service Rates (fetch from UPS or FedEx API)
    if contract_type.lower() == "ups":
        rates = APIRates.get_ups_rates(destination_address, start_address, parcel)
    else:
        rates = APIRates.get_fedex_rates(destination_address, start_address, parcel)

    # Print the API response for debugging
    print("Rates API Response:", rates)

    portfolio_incentives = get_portfolio_tier_incentive(table_data, weekly_price)
    if len(portfolio_incentives) == 0:
        return JSONResponse(content={"success": False, "message": "Failed to find discounts"}, status_code=400)
    discounts = []

    for incentive in portfolio_incentives:
        service_name = incentive.get("service", "")
        service_discount = incentive.get("incentive", 0)
        final_discount = service_discount

        incentive_off_executive = get_incentive_off_executive(table_data, service_name, weekly_price,parcel.weight)
        # Calculate the combined discount
        final_discount = 100 - (100 - service_discount) * (100 - incentive_off_executive) / 100

        service_amount = next(
            (float(rate.get("amount", 0)) for rate in rates if find_best_match(rate.get("serviceName", ""), [service_name])),
            None
        )
        if service_amount is not None:
            applied_discount_rate = round(service_amount * abs(100-final_discount) / 100, 2)
        else:
            applied_discount_rate = None

        print("\nService Name:", service_name)
        print("Service Discount:", service_discount)
        print("Incentive Off Executive:", incentive_off_executive)
        print("Final Discount:", final_discount)
        print("Service Amount:", service_amount)

        maximum_possible_discount = get_maximum_possible_discount(table_data, service_name)
        is_over_discounted = final_discount > maximum_possible_discount
        print("Maximum Possible Discount:", maximum_possible_discount)
        print("Is Over Discounted:", is_over_discounted)

        if service_amount is not None:
            if final_discount == 0:
                final_amount = service_amount
            else:
                final_amount = applied_discount_rate if not is_over_discounted else round(service_amount * (100-maximum_possible_discount) / 100, 2)
        else:
            final_amount = None

        discounts.append({
            "service_name": service_name,
            "service_discount": (maximum_possible_discount if is_over_discounted else final_discount),
            "is_over_discounted": is_over_discounted,
            "base_amount": service_amount,
            "final_amount": final_amount
        })

    return JSONResponse(content={"success": True, "message": "Discount calculated", "data": discounts}, status_code=200)
