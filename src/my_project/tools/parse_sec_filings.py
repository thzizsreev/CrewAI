# parse_sec_filing.py
import os
import json
import re, requests
import xml.etree.ElementTree as ET

class SECFilingParser:
    def extract_xml_block(self, text: str) -> str:
        """Extract the <ownershipDocument> ... </ownershipDocument> block."""
        match = re.search(r"<ownershipDocument.*?</ownershipDocument>", text, re.S)
        if not match:
            raise ValueError("No <ownershipDocument> block found")
        return match.group(0)

    def parse_sec_filing(self, content):
        
        print("Parsing filing content...")
        xml_block = self.extract_xml_block(content)
        root = ET.fromstring(xml_block)

        filing = {}

        # Filing metadata
        filing["form_type"] = root.findtext("documentType")
        filing["period_of_report"] = root.findtext("periodOfReport")
        print(f"Form Type: {filing['form_type']}, Period: {filing['period_of_report']}")

        # Issuer
        issuer = root.find("issuer")
        filing["issuer"] = {
            "cik": issuer.findtext("issuerCik"),
            "name": issuer.findtext("issuerName"),
            "symbol": issuer.findtext("issuerTradingSymbol"),
        }

        # Reporting Owner
        owner = root.find("reportingOwner")
        filing["reporting_owner"] = {
            "cik": owner.find("reportingOwnerId/rptOwnerCik").text,
            "name": owner.find("reportingOwnerId/rptOwnerName").text,
            "is_director": owner.findtext("reportingOwnerRelationship/isDirector") == "1",
            "is_officer": owner.findtext("reportingOwnerRelationship/isOfficer") == "1",
            "is_ten_percent_owner": owner.findtext("reportingOwnerRelationship/isTenPercentOwner") == "1",
            "is_other": owner.findtext("reportingOwnerRelationship/isOther") == "1",
        }

        # Non-derivative holdings
        non_derivatives = []
        for nd in root.findall(".//nonDerivativeHolding"):
            non_derivatives.append({
                "security": nd.findtext("securityTitle/value"),
                "shares": nd.findtext("postTransactionAmounts/sharesOwnedFollowingTransaction/value"),
                "ownership": nd.findtext("ownershipNature/directOrIndirectOwnership/value"),
                "ownership_note": (
                    nd.findtext("ownershipNature/natureOfOwnership/value")
                    if nd.find("ownershipNature/natureOfOwnership/value") is not None else None
                )
            })
        filing["non_derivative_holdings"] = non_derivatives

        # Derivative transactions
        derivative_transactions = []
        for dt in root.findall(".//derivativeTransaction"):
            derivative_transactions.append({
                "security": dt.findtext("securityTitle/value"),
                "transaction_date": dt.findtext("transactionDate/value"),
                "shares": dt.findtext("transactionAmounts/transactionShares/value"),
                "price": dt.findtext("transactionAmounts/transactionPricePerShare/value"),
                "code": dt.findtext("transactionCoding/transactionCode"),
                "acquired_disposed": dt.findtext("transactionAmounts/transactionAcquiredDisposedCode/value"),
                "exercise_date": dt.findtext("exerciseDate/value"),
                "expiration_date": dt.findtext("expirationDate/value"),
                "post_transaction_shares": dt.findtext("postTransactionAmounts/sharesOwnedFollowingTransaction/value"),
                "ownership": dt.findtext("ownershipNature/directOrIndirectOwnership/value"),
            })
        filing["derivative_transactions"] = derivative_transactions

        # Derivative holdings
        derivative_holdings = []
        for dh in root.findall(".//derivativeHolding"):
            derivative_holdings.append({
                "security": dh.findtext("securityTitle/value"),
                "exercise_price": dh.findtext("conversionOrExercisePrice/value"),
                "exercise_date": dh.findtext("exerciseDate/value"),
                "expiration_date": dh.findtext("expirationDate/value"),
                "underlying_shares": dh.findtext("underlyingSecurity/underlyingSecurityShares/value"),
                "ownership": dh.findtext("ownershipNature/directOrIndirectOwnership/value"),
            })
        filing["derivative_holdings"] = derivative_holdings

        # Footnotes
        footnotes = {}
        for fn in root.findall(".//footnote"):
            fid = fn.attrib.get("id")
            footnotes[fid] = fn.text.strip() if fn.text else ""
        filing["footnotes"] = footnotes

        # Signature
        filing["signature"] = {
            "name": root.findtext("ownerSignature/signatureName"),
            "date": root.findtext("ownerSignature/signatureDate"),
        }
        
        with open("contents_urls.txt", "a", encoding="utf8") as tf:
            tf.write(f"Form Type: {filing['form_type']}\n")
            tf.write(f"Period of Report: {filing['period_of_report']}\n")
            tf.write(f"Issuer: {filing['issuer']['name']} ({filing['issuer']['symbol']})\n")
            tf.write(f"Reporting Owner: {filing['reporting_owner']['name']}\n")
            tf.write("Non-derivative Holdings:\n")
            for nd in filing["non_derivative_holdings"]:
                tf.write(f"  - {nd['security']}: {nd['shares']} shares ({nd['ownership']})\n")
            tf.write("Derivative Transactions:\n")
            for dt in filing["derivative_transactions"]:
                tf.write(f"  - {dt['transaction_date']}: {dt['shares']} {dt['security']} at {dt['price']} ({dt['code']})\n")
            tf.write("Derivative Holdings:\n")
            for dh in filing["derivative_holdings"]:
                tf.write(f"  - {dh['security']} {dh['underlying_shares']} shares, exp {dh['expiration_date']}\n")
            tf.write("Footnotes:\n")
            for fid, text in filing["footnotes"].items():
                tf.write(f"  {fid}: {text}\n")
            tf.write(f"Signature: {filing['signature']['name']} on {filing['signature']['date']}\n")
            tf.write("\n---------------------------------------------------------\n\n")

        
        return filing
    
    def collect_txt(self, file_url):
        resp = requests.get(file_url, headers={"User-Agent": "MyApp/1.0"})
        if resp.status_code != 200:
            raise ValueError(f"Failed to download {file_url}: Status {resp.status_code}")
        return resp.text

    def process_filings(self):
        with open("test.json", "r", encoding="utf8") as f:
            data = json.load(f)
        filings = []

        with open("contents_urls.txt", "w", encoding="utf8") as tf:
            tf.write("================ New Filing =================\n")

        for entry in data:
            file_url = entry.get("link")
            if not file_url:
                print(f"Skipping entry ID {entry.get('id', 'N/A')}: No link found.")
                continue
            try:
                text = self.collect_txt(file_url)
                filing = self.parse_sec_filing(text)
                filings.append(filing)
            except Exception as e:
                print(f"Error processing {file_url}: {e}")

        
        return filings

        # return filings
