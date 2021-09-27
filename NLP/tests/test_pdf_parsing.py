
import pandas as pd

from nationbetter.pdf import download
from nationbetter.pdf import layout_parsing
from nationbetter.pdf import page_parsing

pdf_links = [
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/900030/2020-07-13_Tier_2_Policy_Guidance.pdf",
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/901455/2020-07-16_Tier-2-5-sponsor-guidance_Jul-2020_v1.0.pdf",
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/878155/2020-04-03_Sponsor-guidance_Appendix-A_04-2020_v1.0.pdf",
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/255350/sponsorguideappBfrom060412.pdf",
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/878156/2020-04-03_Sponsor-guidance_Appendix-D_04-2020_v1.0.pdf", "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/795425/Final_Tier_5_Temporary_Worker_Guidance_05-04-19.pdf",
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/891368/calculating-continuous-leave-v21.0-gov-uk.pdf",
"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/870839/english-language-v17.0ext.pdf"
]

# create folder and download pdf files
download.create_folder("input")
file_names= pdf_download.download_pdfs(pdf_links)
print(file_names)

# perform layout analysis
dict_layout = layout_parsing.get_lines_and_info(file_names[1])

# create layout dataframe
df_layout = pd.DataFrame(dict_layout)

# perform page analysis (?)
df_annot, df_content, df_data = page_parsing.build_pdf_df(file_name[1])
