"""Shared cleaning maps for the Veltrix project.

Keep this file in `notebooks/` and import it from every notebook, so there is ONE definition of each mapping.
Share it with the DA team: their SQL CASE mappings (Day 4) must give the same result.
"""

# ---------------------------------------------------------------------------------------------
# Lead source: 28 raw spellings -> 14 clean channels (the README says 14 spellings are inconsistent).
# Checked against the raw values and counts in the lead_source profile.
#
# TO CONFIRM with the DA team:
#   "Google"  -> Google Ads   (assumed; there is no separate organic-search channel in the data)
#   "Website" -> Veltrix website (assumed to be Veltrix's own site)
# ---------------------------------------------------------------------------------------------
LEAD_SOURCE_MAP = {
    "Rightmove": "Rightmove", "Right Move": "Rightmove", "RightMove": "Rightmove", "rightmove": "Rightmove",
    "Zoopla": "Zoopla", "zoopla": "Zoopla", "Zoopla.co.uk": "Zoopla",
    "OnTheMarket": "OnTheMarket", "On The Market": "OnTheMarket", "OTM": "OnTheMarket",
    "Veltrix website": "Veltrix website", "veltrix.co.uk": "Veltrix website", "Website": "Veltrix website",
    "Referral": "Referral",
    "Google Ads": "Google Ads", "google ads": "Google Ads", "Google": "Google Ads",
    "Email newsletter": "Email newsletter",
    "Facebook": "Facebook", "FB": "Facebook",
    "Instagram": "Instagram", "Insta": "Instagram",
    "TikTok": "TikTok",
    "Branch walk-in": "Branch walk-in", "Walk-in": "Branch walk-in",
    "Overseas agent partner": "Overseas agent partner",
    "Relocation partner": "Relocation partner",
    "WeChat": "WeChat",
}

# ---------------------------------------------------------------------------------------------
# Country labels -> ISO 3166-1 alpha-2.
# Checked against the real country_of_residence labels. The cleaning notebook stops and lists any label
# missing here, so nothing is silently left unmapped. The last four added after that stop were
# Mainland China, PRC, SG and U.A.E. Seen in the data: United Kingdom, UK, England, Great Britain, U.K., Scotland, Wales, Hong Kong, HK, Hong Kong SAR,
# United Arab Emirates, UAE, India, Nigeria, Singapore, China, United States, USA, US, Canada, Malaysia, Saudi Arabia, Qatar.
# ---------------------------------------------------------------------------------------------
COUNTRY_MAP = {
    "United Kingdom": "GB", "UK": "GB", "U.K.": "GB", "England": "GB", "Great Britain": "GB",
    "Scotland": "GB", "Wales": "GB", "Northern Ireland": "GB", "GB": "GB",
    "Hong Kong": "HK", "Hong Kong SAR": "HK", "HK": "HK",
    "United Arab Emirates": "AE", "UAE": "AE", "U.A.E.": "AE",
    "Saudi Arabia": "SA", "KSA": "SA",
    "China": "CN", "Mainland China": "CN", "PRC": "CN", "Nigeria": "NG", "India": "IN", "Singapore": "SG", "SG": "SG", "Pakistan": "PK",
    "Ireland": "IE", "United States": "US", "USA": "US", "US": "US", "Canada": "CA", "Australia": "AU",
    "Qatar": "QA", "Kuwait": "KW", "Malaysia": "MY", "Kenya": "KE", "South Africa": "ZA",
    "Germany": "DE", "France": "FR", "Spain": "ES", "Netherlands": "NL", "The Netherlands": "NL", "Holland": "NL",
}
