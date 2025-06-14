import pdfplumber

def main():
    with pdfplumber.open("StundenplanHS2025-26.pdf") as pdf:
        for p in pdf.pages:
            for t in p.extract_tables():
                for r in t:
                    print(r)

if __name__ == "__main__":
    main()
