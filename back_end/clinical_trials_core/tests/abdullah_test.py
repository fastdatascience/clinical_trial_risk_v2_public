import os

from clinicaltrials.core import ClinicalTrial, Document

# ct = ClinicalTrial()
# print(ct.modules)
# print(ct.modules_len)
# print(ct.metadata)
# print(ct.metadata_dict)

exit()

dir_path = os.path.dirname(os.path.realpath(__file__))
document = Document.pdf_to_document(pdf_path=f"{dir_path}/example_tiny_pdf_file.pdf")

pdf_path = os.path.join(dir_path, "example_tiny_pdf_file.pdf")


with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

document.pages[0].marker.add_highlight("sample size")

for marker in document.pages[0].marker.markers:
    print(marker)

Document.add_document_highlights(pdf_buffer=pdf_bytes, document=document, save_to_disk=True)

# document = Document.pdf_to_document(pdf_path="/home/awr417h/Downloads/Prot_SAP_ICF_000.pdf")

# for page in document.pages:
#     if page.tables:
#         print(page.tables)

# print(document.metadata)
# print(document.pages)

# d = ct.get_module("drug")

# d_result = d.process(document=document)

# phase = ct.get_module("phase")
# print(phase)
# phase.process(document=document)

# results = ct.run_all(document=document)
# print(results)

# results = ct.run_all(document=document, exclude_modules=["num_arms"], parallel=True)
# print(results)
