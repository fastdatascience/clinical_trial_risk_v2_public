import json
from collections import Counter

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page


class NumInterventionsPerVisit(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="num_interventions_per_visit", name="Number of interventions or investigations per visit, according to the Schedule of Events", feature_type="numeric", )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        num_interventions_per_visit = 0
        occurrence_to_pages = {}
        for page_no, page in enumerate(document.pages):
            if len(page.tables) > 0:
                ctr_total = Counter()
                col_counters = {}
                for table in page.tables:
                    for row in table:
                        for col_idx, cell in enumerate(row):
                            if col_idx not in col_counters:
                                col_counters[col_idx] = Counter()
                            col_counter = col_counters[col_idx]
                            if cell is None:
                                continue
                            if cell.upper().startswith("X") or cell.startswith("✓") or cell.startswith("×"):
                                cell = "X"
                            ctr_total[cell] += 1
                            col_counter[cell] += 1
                            if col_counter["X"] > 0:
                                num_interventions_per_visit = max([col_counter["X"], num_interventions_per_visit])

                            match_text_norm = "Schedule of events"
                            if match_text_norm not in occurrence_to_pages:
                                occurrence_to_pages[match_text_norm] = []
                            occurrence_to_pages[match_text_norm].append(page_no)
        return {"prediction": num_interventions_per_visit, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = NumInterventionsPerVisit()
    document = Document([Page(
        content="HVTN 114, Version 1.0 / June 20, 2016\nAppendix F Laboratory procedures\nTube volume (mL)\nVisit: 1 2 3 4 5 6 7 8 9\nDay: D0 D7 D14 D112 D119 D126 D196 D303\nMonth: Screening visit3 M0 M0.25 M0.5 M4 4.25 M4.5 M7 M10\nVAC1 VAC2\nTube size (vol.\nProcedure Ship to1, 2 Assay Location2 Tube4 capacity)4 Total\nBLOOD COLLECTION\nScreening or diagnostic assays\nHBsAg/anti-HCV Local Lab Local Lab SST 5mL 5 — — — — — — — — 5\nSyphilis Local Lab Local Lab SST 5mL 5 511 — 511 511 — 511 — 511 30\nHIV diagnostics9 UW-VSL UW-VSL EDTA 10mL 10 — — — 10 — — 10 20 50\nSafety labs\nCBC/ Diff/ platelets Local lab Local lab EDTA 5mL 5 — — 5 — — 5 5 — 20\nChemistry panel5 Local lab Local lab SST 5mL 5 — — 5 — — 5 5 — 20\nCardiac Troponin6 Local lab Local lab Na Hep 5mL 5 — — 5 — — 5 — — 15\nImmunogenicity assays7\nHumoral assays\nHIV-1 binding Ab CSR Duke SST 8.5mL — 8.5 — 8.5 8.5 — 8.5 8.5 8.5 51\nNeutralizing Ab CSR Duke SST 8.5mL — 8.5 — 8.5 8.5 — 8.5 8.5 8.5 51\nAb avidity CSR Duke SST 8.5mL — y — y y — y y y 0\nADCC CSR Duke SST 8.5mL — y — y y — y y y 0\nCellular assays\nHIV-specific ICS CSR FHCRC ACD 8.5mL — 42.5 — 42.5 — — 42.5 — 42.5 170\nPhenotyping (pTfh) CSR FHCRC ACD 8.5mL — — 17 — — 17 — — — 34\nSpecimen storage\nPBMC CSR ACD 8.5mL — 42.5 — 68 — — 68 — 68 246.5 check\nSerum CSR SST 8.5mL — 51 — 34 34 — 34 34 34 221 913.5\nVisit total 35 158 17 181.5 66 17 181.5 71 186.5 913.5\n56-Day total 35 193 210 391.5 66 83 264.5 71 186.5\nURINE COLLECTION\nUrinalysis Local lab Local lab X — — X — — X — —\nPregnancy test8 Local lab Local lab X X — X10 X — X10 X X10\nChlamydia/Gonorrhea11 Local lab Local lab — X — — — — X — —\nCERVICAL/VAGINAL SWAB COLLECTION12\nTrichomonas vaginalis Local lab Local lab — X — X X — X — X\nBacterial vaginosis Local lab Local lab — X — X X — X — X\nYeast Local lab Local lab — X — X X — X — X\nMUCOSAL SAMPLE COLLECTION (OPTIONAL)11\nSemen CSR Duke — X — X X — X — X\nCervical secretion CSR Duke — X — X X — X — X\nRectal secretion CSR Duke — X — X X — X — X\nHVTN114_v1-0_FINAL / Page 120 of 125",
        tables=[[["Visit:\nDay:\nMonth:\nTube size (vol.\nProcedure Ship to1, 2 Assay Location2 Tube4 capacity)4", None,
                  None, None, None, "Tube volume (mL)", None, None, None, None, None, None, None, None, "Total"],
                 [None, None, None, None, None, "1", "2", "3", "4", "5", "6", "7", "8", "9", None],
                 [None, None, None, None, None, "Screening visit3", "D0", "D7", "D14", "D112", "D119", "D126", "D196",
                  "D303", None],
                 [None, None, None, None, None, None, "M0", "M0.25", "M0.5", "M4", "4.25", "M4.5", "M7", "M10", None],
                 [None, None, None, None, None, "", "VAC1", "", "", "VAC2", "", "", "", "", None],
                 [None, None, None, None, None, "", "", "", "", "", "", "", "", "", None],
                 ["BLOOD COLLECTION", None, None, None, None, None, None, None, None, None, None, None, None, None,
                  None],
                 ["Screening or diagnostic assays", None, None, None, None, None, None, None, None, None, None, None,
                  None, None, None],
                 ["HBsAg/anti-HCV", "Local Lab", "Local Lab", "SST", "5mL", "5", "\u2014", "\u2014", "\u2014", "\u2014",
                  "\u2014", "\u2014", "\u2014", "\u2014", "5"],
                 ["Syphilis", "Local Lab", "Local Lab", "SST", "5mL", "5", "511", "\u2014", "511", "511", "\u2014",
                  "511", "\u2014", "511", "30"],
                 ["HIV diagnostics9", "UW-VSL", "UW-VSL", "EDTA", "10mL", "10", "\u2014", "\u2014", "\u2014", "10",
                  "\u2014", "\u2014", "10", "20", "50"],
                 ["Safety labs", None, None, None, "", "", None, None, None, None, None, None, None, None, None],
                 ["CBC/ Diff/ platelets", "Local lab", "Local lab", "EDTA", "5mL", "5", "\u2014", "\u2014", "5",
                  "\u2014", "\u2014", "5", "5", "\u2014", "20"],
                 ["Chemistry panel5", "Local lab", "Local lab", "SST", "5mL", "5", "\u2014", "\u2014", "5", "\u2014",
                  "\u2014", "5", "5", "\u2014", "20"],
                 ["Cardiac Troponin6", "Local lab", "Local lab", "Na Hep", "5mL", "5", "\u2014", "\u2014", "5",
                  "\u2014", "\u2014", "5", "\u2014", "\u2014", "15"],
                 ["Immunogenicity assays7", None, None, None, "", "", None, None, None, None, None, None, None, None,
                  None],
                 ["Humoral assays", None, None, None, "", "", None, None, None, None, None, None, None, None, ""],
                 ["HIV-1 binding Ab", "CSR", "Duke", "SST", "8.5mL", "\u2014", "8.5", "\u2014", "8.5", "8.5", "\u2014",
                  "8.5", "8.5", "8.5", "51"],
                 ["Neutralizing Ab", "CSR", "Duke", "SST", "8.5mL", "\u2014", "8.5", "\u2014", "8.5", "8.5", "\u2014",
                  "8.5", "8.5", "8.5", "51"],
                 ["Ab avidity", "CSR", "Duke", "SST", "8.5mL", "\u2014", "y", "\u2014", "y", "y", "\u2014", "y", "y",
                  "y", "0"],
                 ["ADCC", "CSR", "Duke", "SST", "8.5mL", "\u2014", "y", "\u2014", "y", "y", "\u2014", "y", "y", "y",
                  "0"], ["Cellular assays", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                 ["HIV-specific ICS", "CSR", "FHCRC", "ACD", "8.5mL", "\u2014", "42.5", "\u2014", "42.5", "\u2014",
                  "\u2014", "42.5", "\u2014", "42.5", "170"],
                 ["Phenotyping (pTfh)", "CSR", "FHCRC", "ACD", "8.5mL", "\u2014", "\u2014", "17", "\u2014", "\u2014",
                  "17", "\u2014", "\u2014", "\u2014", "34"],
                 ["Specimen storage", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                 ["PBMC", "CSR", "", "ACD", "8.5mL", "\u2014", "42.5", "\u2014", "68", "\u2014", "\u2014", "68",
                  "\u2014", "68", "246.5"],
                 ["Serum", "CSR", "", "SST", "8.5mL", "\u2014", "51", "\u2014", "34", "34", "\u2014", "34", "34", "34",
                  "221"],
                 ["Visit total", None, None, None, "", "35", "158", "17", "181.5", "66", "17", "181.5", "71", "186.5",
                  "913.5"],
                 ["56-Day total", None, None, None, "", "35", "193", "210", "391.5", "66", "83", "264.5", "71", "186.5",
                  ""],
                 ["URINE COLLECTION", None, None, "", "", "", None, None, None, None, None, None, None, None, None],
                 ["Urinalysis", "Local lab", "Local lab", "", "", "X", "\u2014", "\u2014", "X", "\u2014", "\u2014", "X",
                  "\u2014", "\u2014", ""],
                 ["Pregnancy test8", "Local lab", "Local lab", "", "", "X", "X", "\u2014", "X10", "X", "\u2014", "X10",
                  "X", "X10", ""],
                 ["Chlamydia/Gonorrhea11", "Local lab", "Local lab", "", "", "\u2014", "X", "\u2014", "\u2014",
                  "\u2014", "\u2014", "X", "\u2014", "\u2014", ""],
                 ["CERVICAL/VAGINAL SWAB COLLECTION12", None, None, "", "", "", None, None, None, None, None, None,
                  None, None, None],
                 ["Trichomonas vaginalis", "Local lab", "Local lab", "", "", "\u2014", "X", "\u2014", "X", "X",
                  "\u2014", "X", "\u2014", "X", ""],
                 ["Bacterial vaginosis", "Local lab", "Local lab", "", "", "\u2014", "X", "\u2014", "X", "X", "\u2014",
                  "X", "\u2014", "X", ""],
                 ["Yeast", "Local lab", "Local lab", "", "", "\u2014", "X", "\u2014", "X", "X", "\u2014", "X", "\u2014",
                  "X", ""],
                 ["MUCOSAL SAMPLE COLLECTION (OPTIONAL)11", None, None, "", "", "", None, None, None, None, "", "",
                  None, None, None],
                 ["Semen", "CSR", "Duke", "", "", "\u2014", "X", "\u2014", "X", "X", "\u2014", "X", "\u2014", "X", ""],
                 ["Cervical secretion", "CSR", "Duke", "", "", "\u2014", "X", "\u2014", "X", "X", "\u2014", "X",
                  "\u2014", "X", ""],
                 ["Rectal secretion", "CSR", "Duke", "", "", "\u2014", "X", "\u2014", "X", "X", "\u2014", "X", "\u2014",
                  "X", ""]]], page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
