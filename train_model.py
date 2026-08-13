"""
╔══════════════════════════════════════════════════════════════╗
║   SchemeSaathi - ML Model Trainer                           ║
║   Trains 3 ML models:                                       ║
║   1. TF-IDF + Cosine Similarity  → Search                   ║
║   2. Random Forest Classifier    → Eligibility              ║
║   3. TF-IDF Vectorizer           → Chatbot intent matching  ║
╚══════════════════════════════════════════════════════════════╝
Run: python train_model.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ─────────────────────────────────────────────────────────────────
# 1. COMPLETE SCHEME DATABASE  (30 schemes across 6 categories)
# ─────────────────────────────────────────────────────────────────

SCHEMES = [
  {
    "id": 1, "name": "PM-KISAN",
    "full": "Pradhan Mantri Kisan Samman Nidhi",
    "cat": "farmer",
    "desc": "Direct income support of Rs 6000 per year to small marginal farmers in three equal instalments of Rs 2000 each. Money transferred directly to bank account. Helps farmers buy seeds fertilizers and meet farming needs.",
    "eligibility": "Farmers owning cultivable land below 2 hectares",
    "ministry": "Agriculture & Farmers Welfare",
    "benefit": "Rs 6,000/year direct bank transfer",
    "age_min": 18, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer"],
    "residence": ["Rural","Semi-Urban"],
    "bpl_required": False,
    "link": "https://pmkisan.gov.in",
    "tags": "kisan farmer agriculture income support direct benefit transfer land"
  },
  {
    "id": 2, "name": "Ayushman Bharat PM-JAY",
    "full": "Pradhan Mantri Jan Arogya Yojana",
    "cat": "health",
    "desc": "Health insurance coverage of Rs 5 lakh per family per year for secondary and tertiary care hospitalization. Covers pre existing diseases. Cashless treatment at empanelled hospitals. Covers 1393 medical procedures.",
    "eligibility": "Economically weaker sections from SECC-2011 database, BPL families",
    "ministry": "Health & Family Welfare",
    "benefit": "Rs 5 Lakh/year health cover per family",
    "age_min": 0, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 250000,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": True,
    "link": "https://pmjay.gov.in",
    "tags": "health insurance hospital medical treatment cashless poor family"
  },
  {
    "id": 3, "name": "PMAY",
    "full": "Pradhan Mantri Awas Yojana",
    "cat": "housing",
    "desc": "Financial assistance and subsidy for construction or purchase of pucca houses. For homeless and those living in kutcha temporary houses. Covers both rural PMAY-G and urban PMAY-U beneficiaries.",
    "eligibility": "Homeless families, those in kutcha houses, EWS/LIG/MIG income groups",
    "ministry": "Housing & Urban Affairs",
    "benefit": "Up to Rs 2.67 Lakh interest subsidy",
    "age_min": 18, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 600000,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed","Salaried"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "https://pmaymis.gov.in",
    "tags": "housing house construction pucca home rural urban subsidy shelter"
  },
  {
    "id": 4, "name": "MGNREGA",
    "full": "Mahatma Gandhi National Rural Employment Guarantee Act",
    "cat": "employment",
    "desc": "Guarantees 100 days of wage employment per year to every rural household. Adult members do unskilled manual work. Wages paid within 15 days. Employment within 5km of residence. Unemployment allowance if work not provided.",
    "eligibility": "Adult rural residents willing to do unskilled manual work",
    "ministry": "Rural Development",
    "benefit": "100 days guaranteed employment per year",
    "age_min": 18, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 300000,
    "occupation": ["Daily Wage Worker","Unemployed","Farmer"],
    "residence": ["Rural","Semi-Urban"],
    "bpl_required": False,
    "link": "https://nrega.nic.in",
    "tags": "employment work rural jobs wage guarantee unskilled manual labour 100 days"
  },
  {
    "id": 5, "name": "Beti Bachao Beti Padhao",
    "full": "Beti Bachao Beti Padhao Scheme",
    "cat": "women",
    "desc": "Scheme to save and educate the girl child. Addresses declining child sex ratio. Promotes welfare and education of girl child. Covers awareness campaigns healthcare and education support for girls.",
    "eligibility": "Girl children especially in districts with low sex ratio",
    "ministry": "Women & Child Development",
    "benefit": "Education support and welfare programs",
    "age_min": 0, "age_max": 18,
    "gender": ["Female"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "girl child education women welfare daughter save educate sex ratio"
  },
  {
    "id": 6, "name": "Sukanya Samriddhi Yojana",
    "full": "Sukanya Samriddhi Yojana",
    "cat": "women",
    "desc": "Small savings scheme for girl child. High interest rate currently 8.2 percent per annum. Tax deduction under 80C. Account matures when girl turns 21 years. Can be opened for girl below 10 years. For education and marriage expenses.",
    "eligibility": "Parents or guardians of girl child below 10 years of age",
    "ministry": "Finance",
    "benefit": "8.2% interest p.a. + Tax benefits under 80C",
    "age_min": 0, "age_max": 10,
    "gender": ["Female"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "girl savings interest tax education marriage sukanya daughter future"
  },
  {
    "id": 7, "name": "SC/ST Scholarship",
    "full": "Post Matric Scholarship for SC/ST Students",
    "cat": "education",
    "desc": "Financial assistance to Scheduled Caste and Scheduled Tribe students studying at post matric level Class 11 onwards. Covers tuition fees maintenance allowance and other educational costs. State government scheme centrally sponsored.",
    "eligibility": "SC/ST students studying post-matric, family income below Rs 2.5 Lakh per annum",
    "ministry": "Social Justice & Empowerment",
    "benefit": "Full tuition fee + maintenance allowance",
    "age_min": 14, "age_max": 40,
    "gender": ["Male","Female","Transgender"],
    "category": ["SC","ST"],
    "income_max": 250000,
    "occupation": ["Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "https://scholarships.gov.in",
    "tags": "scholarship SC ST education student tuition fees financial assistance"
  },
  {
    "id": 8, "name": "PM Fasal Bima",
    "full": "Pradhan Mantri Fasal Bima Yojana",
    "cat": "farmer",
    "desc": "Comprehensive crop insurance scheme for farmers. Covers losses from natural calamities drought flood pest attack. Very low premium only 2 percent for Kharif crops and 1.5 percent for Rabi crops. Covers pre sowing to post harvest period.",
    "eligibility": "All farmers growing notified crops in notified areas",
    "ministry": "Agriculture & Farmers Welfare",
    "benefit": "Crop loss compensation at sum insured",
    "age_min": 18, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer"],
    "residence": ["Rural","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "crop insurance farmer agriculture loss flood drought natural disaster kharif rabi"
  },
  {
    "id": 9, "name": "Ujjwala Yojana",
    "full": "Pradhan Mantri Ujjwala Yojana",
    "cat": "women",
    "desc": "Free LPG connection to women from BPL households. Aims to replace unhealthy cooking fuel wood kerosene with clean LPG gas. Reduces indoor air pollution. Protects health of women and children. Free first cylinder and subsidized refills.",
    "eligibility": "Women aged 18 and above from BPL families without prior LPG connection",
    "ministry": "Petroleum & Natural Gas",
    "benefit": "Free LPG connection + first cylinder",
    "age_min": 18, "age_max": 99,
    "gender": ["Female"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 200000,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": True,
    "link": "",
    "tags": "LPG gas cooking fuel women BPL poor free connection ujjwala"
  },
  {
    "id": 10, "name": "Stand Up India",
    "full": "Stand Up India Scheme",
    "cat": "employment",
    "desc": "Bank loans between Rs 10 Lakh to Rs 1 Crore for SC ST borrowers and women entrepreneurs. For setting up greenfield enterprises in manufacturing services or trading. Repayment period up to 7 years. Covers composite loan.",
    "eligibility": "SC/ST or Women entrepreneurs, greenfield projects, aged above 18",
    "ministry": "Finance",
    "benefit": "Loan Rs 10 Lakh to Rs 1 Crore",
    "age_min": 18, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Self-employed","Unemployed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "loan business entrepreneur SC ST women startup enterprise bank"
  },
  {
    "id": 11, "name": "MUDRA Yojana",
    "full": "Pradhan Mantri MUDRA Yojana",
    "cat": "employment",
    "desc": "Micro loans for small businesses without collateral. Three categories Shishu up to Rs 50000 Kishore Rs 50001 to Rs 5 Lakh Tarun Rs 5 Lakh to Rs 10 Lakh. For non farm income generating activities.",
    "eligibility": "Small business owners, entrepreneurs, artisans, traders, vendors",
    "ministry": "Finance",
    "benefit": "Loans up to Rs 10 Lakh without collateral",
    "age_min": 18, "age_max": 65,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Self-employed","Daily Wage Worker","Unemployed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "MUDRA loan business micro finance small enterprise no collateral"
  },
  {
    "id": 12, "name": "NSP Scholarships",
    "full": "National Scholarship Portal",
    "cat": "education",
    "desc": "Single platform for all central and state government scholarship schemes. For students from pre matric to post doctoral level. Based on academic merit and family income. Covers minority OBC SC ST and disabled students.",
    "eligibility": "Students across all levels based on category and income criteria",
    "ministry": "Education",
    "benefit": "Various stipends and tuition support",
    "age_min": 6, "age_max": 35,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 350000,
    "occupation": ["Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "https://scholarships.gov.in",
    "tags": "scholarship NSP student education tuition minority OBC SC ST stipend"
  },
  {
    "id": 13, "name": "PM SVANidhi",
    "full": "PM Street Vendor's AtmaNirbhar Nidhi",
    "cat": "employment",
    "desc": "Micro loans for street vendors to restart businesses affected by COVID-19. Initial loan of Rs 10000 graduating to Rs 20000 and Rs 50000. No collateral needed. Builds credit history for vendors.",
    "eligibility": "Street vendors with vending certificate or identity card",
    "ministry": "Housing & Urban Affairs",
    "benefit": "Loans Rs 10,000 to Rs 50,000",
    "age_min": 18, "age_max": 65,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 300000,
    "occupation": ["Self-employed","Daily Wage Worker"],
    "residence": ["Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "street vendor hawker loan micro credit SVANidhi urban small business"
  },
  {
    "id": 14, "name": "Old Age Pension IGNOAPS",
    "full": "Indira Gandhi National Old Age Pension Scheme",
    "cat": "social",
    "desc": "Monthly pension for elderly poor people above 60 years. Rs 200 per month for age 60 to 79 and Rs 500 per month for age 80 and above. State governments often add their own contribution.",
    "eligibility": "BPL persons aged 60 years and above",
    "ministry": "Rural Development",
    "benefit": "Rs 200-500/month pension",
    "age_min": 60, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 150000,
    "occupation": ["Senior Citizen","Unemployed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": True,
    "link": "",
    "tags": "pension old age senior citizen elderly monthly allowance BPL"
  },
  {
    "id": 15, "name": "Widow Pension IGNWPS",
    "full": "Indira Gandhi National Widow Pension Scheme",
    "cat": "social",
    "desc": "Monthly pension for destitute widows aged 40 to 59 years from BPL households. Central government provides Rs 300 per month. States often top up this amount. Helps widows become financially independent.",
    "eligibility": "Widows aged 40-59 years from BPL households",
    "ministry": "Rural Development",
    "benefit": "Rs 300/month pension",
    "age_min": 40, "age_max": 59,
    "gender": ["Female"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 150000,
    "occupation": ["Unemployed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": True,
    "link": "",
    "tags": "widow pension women monthly support BPL destitute"
  },
  {
    "id": 16, "name": "Disability Pension IGNDPS",
    "full": "Indira Gandhi National Disability Pension Scheme",
    "cat": "social",
    "desc": "Monthly pension for persons with severe or multiple disabilities aged 18 to 59 years from BPL households. Rs 300 per month from central government. Disability must be 80 percent or more.",
    "eligibility": "Persons with 80%+ disability aged 18-59, BPL households",
    "ministry": "Rural Development",
    "benefit": "Rs 300/month pension",
    "age_min": 18, "age_max": 59,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 150000,
    "occupation": ["Differently Abled"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": True,
    "link": "",
    "tags": "disability pension disabled person handicap BPL monthly support"
  },
  {
    "id": 17, "name": "Maternity Benefit PMMVY",
    "full": "Pradhan Mantri Matru Vandana Yojana",
    "cat": "women",
    "desc": "Cash incentive of Rs 5000 in three installments for first live birth. Compensates wage loss during pregnancy and lactation. Promotes good nutrition and healthy feeding practices. Enrolled through Anganwadi and health centres.",
    "eligibility": "Pregnant and lactating women for first live birth, age 19+",
    "ministry": "Women & Child Development",
    "benefit": "Rs 5,000 cash incentive",
    "age_min": 19, "age_max": 45,
    "gender": ["Female"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "maternity pregnancy women lactation cash incentive mother baby nutrition"
  },
  {
    "id": 18, "name": "PM Kaushal Vikas",
    "full": "Pradhan Mantri Kaushal Vikas Yojana",
    "cat": "employment",
    "desc": "Free skill training for youth. Over 300 job roles across various sectors. Certificate recognized by industry. Placement assistance after training. Monetary reward on certification. Covers retail hospitality healthcare IT and other sectors.",
    "eligibility": "Youth aged 15-45 years, school or college dropouts or unemployed",
    "ministry": "Skill Development & Entrepreneurship",
    "benefit": "Free skill training + Rs 8,000 reward",
    "age_min": 15, "age_max": 45,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 400000,
    "occupation": ["Unemployed","Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "skill training youth employment kaushal certificate job placement vocational"
  },
  {
    "id": 19, "name": "Ration Card NFSA",
    "full": "National Food Security Act - PDS Ration",
    "cat": "social",
    "desc": "Subsidized food grains through Public Distribution System. Priority households get 5 kg per person per month at Rs 2 for wheat and Rs 3 for rice. Antyodaya families get 35 kg per family per month. ONORC one nation one ration card allows portability.",
    "eligibility": "75% rural and 50% urban population covered under NFSA",
    "ministry": "Food & Consumer Affairs",
    "benefit": "Subsidized food grains at Rs 2-3/kg",
    "age_min": 0, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 250000,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": True,
    "link": "",
    "tags": "ration card food grain PDS subsidized rice wheat BPL free food"
  },
  {
    "id": 20, "name": "Jal Jeevan Mission",
    "full": "Jal Jeevan Mission - Har Ghar Jal",
    "cat": "social",
    "desc": "Provides tap water connection to every rural household. Functional household tap connection FHTC with 55 litres per capita per day. Supports water quality testing and school anganwadi connections.",
    "eligibility": "All rural households without tap water connection",
    "ministry": "Jal Shakti",
    "benefit": "Free tap water connection to home",
    "age_min": 0, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed","Salaried"],
    "residence": ["Rural"],
    "bpl_required": False,
    "link": "",
    "tags": "water tap connection rural household jal jeevan mission clean drinking water"
  },
  {
    "id": 21, "name": "PM Jan Dhan",
    "full": "Pradhan Mantri Jan Dhan Yojana",
    "cat": "social",
    "desc": "Zero balance bank account for unbanked poor people. Comes with RuPay debit card. Rs 1 lakh accident insurance cover and Rs 30000 life insurance cover. Overdraft facility up to Rs 10000 after satisfactory operation.",
    "eligibility": "Any Indian citizen aged 10+ without a bank account",
    "ministry": "Finance",
    "benefit": "Free bank account + Rs 1 Lakh insurance",
    "age_min": 10, "age_max": 99,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed","Salaried"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "bank account Jan Dhan zero balance poor unbanked financial inclusion RuPay"
  },
  {
    "id": 22, "name": "PM Suraksha Bima",
    "full": "Pradhan Mantri Suraksha Bima Yojana",
    "cat": "social",
    "desc": "Accidental death and disability insurance at just Rs 20 per year premium. Rs 2 lakh for accidental death or permanent total disability. Rs 1 lakh for partial permanent disability. Bank account required.",
    "eligibility": "Bank account holders aged 18-70 years",
    "ministry": "Finance",
    "benefit": "Rs 2 Lakh accident insurance at Rs 20/year",
    "age_min": 18, "age_max": 70,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed","Salaried"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "accident insurance cheap low premium death disability bank account Rs 20"
  },
  {
    "id": 23, "name": "PM Jeevan Jyoti",
    "full": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
    "cat": "social",
    "desc": "Life insurance cover of Rs 2 lakh at very low premium of Rs 436 per year. Renewed annually. Available to bank account holders. Death benefit payable to nominee. Auto debit from bank account.",
    "eligibility": "Bank account holders aged 18-50 years",
    "ministry": "Finance",
    "benefit": "Rs 2 Lakh life insurance at Rs 436/year",
    "age_min": 18, "age_max": 50,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer","Daily Wage Worker","Unemployed","Self-employed","Salaried"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "life insurance Rs 436 death benefit nominee bank account Jeevan Jyoti"
  },
  {
    "id": 24, "name": "Kisan Credit Card",
    "full": "Kisan Credit Card Scheme",
    "cat": "farmer",
    "desc": "Short term credit for farmers to meet agricultural needs. Covers crop cultivation post harvest expenses maintenance of farm assets and allied activities. Flexible repayment. Low interest rate subsidized by government. Also covers fisheries and animal husbandry.",
    "eligibility": "Farmers, sharecroppers, tenant farmers, SHG members",
    "ministry": "Agriculture & Farmers Welfare",
    "benefit": "Credit up to Rs 3 Lakh at subsidized interest",
    "age_min": 18, "age_max": 75,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer"],
    "residence": ["Rural","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "kisan credit card farmer loan agriculture crop cultivation credit"
  },
  {
    "id": 25, "name": "OBC Scholarship",
    "full": "Pre & Post Matric Scholarship for OBC Students",
    "cat": "education",
    "desc": "Financial support to Other Backward Class students to pursue higher education. Covers pre matric and post matric studies. Maintenance allowance and study fees. Family income limit Rs 1 lakh for pre matric and Rs 2.5 lakh for post matric.",
    "eligibility": "OBC students, family income below Rs 1-2.5 Lakh",
    "ministry": "Social Justice & Empowerment",
    "benefit": "Tuition + maintenance allowance",
    "age_min": 10, "age_max": 35,
    "gender": ["Male","Female","Transgender"],
    "category": ["OBC"],
    "income_max": 250000,
    "occupation": ["Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "https://scholarships.gov.in",
    "tags": "OBC scholarship education student backward class tuition stipend"
  },
  {
    "id": 26, "name": "PMEGP",
    "full": "Prime Minister's Employment Generation Programme",
    "cat": "employment",
    "desc": "Subsidy and loan for setting up micro enterprises. For unemployed youth and traditional artisans. Up to 35 percent subsidy for rural areas and 25 percent for urban areas. Bank loan with government subsidy. Maximum project cost Rs 50 lakh for manufacturing.",
    "eligibility": "Any person above 18 years with minimum 8th class pass for projects above Rs 10 Lakh",
    "ministry": "MSME",
    "benefit": "25-35% government subsidy on project cost",
    "age_min": 18, "age_max": 55,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 500000,
    "occupation": ["Unemployed","Self-employed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "PMEGP enterprise subsidy loan business manufacture rural employment generation"
  },
  {
    "id": 27, "name": "Atal Pension Yojana",
    "full": "Atal Pension Yojana",
    "cat": "social",
    "desc": "Guaranteed minimum pension of Rs 1000 to Rs 5000 per month after age 60. For unorganised sector workers. Government contributes 50 percent of subscriber contribution. Nominee gets same pension after subscriber death.",
    "eligibility": "Unorganised sector workers aged 18-40, bank account holders",
    "ministry": "Finance",
    "benefit": "Rs 1,000-5,000/month pension after age 60",
    "age_min": 18, "age_max": 40,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Farmer","Daily Wage Worker","Self-employed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "pension retirement Atal Pension Yojana unorganised sector monthly pension after 60"
  },
  {
    "id": 28, "name": "PMSBY",
    "full": "PM Scholarship for Central Armed Police Forces",
    "cat": "education",
    "desc": "Scholarship for wards of CAPF personnel who died or were disabled in action. Rs 3000 per month for boys and Rs 3500 per month for girls. For professional degree courses in first year.",
    "eligibility": "Children of CAPF/Assam Rifles personnel",
    "ministry": "Home Affairs",
    "benefit": "Rs 3,000-3,500/month scholarship",
    "age_min": 17, "age_max": 25,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Student"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "https://scholarships.gov.in",
    "tags": "CAPF scholarship police armed forces children education monthly"
  },
  {
    "id": 29, "name": "e-SHRAM",
    "full": "e-SHRAM Portal for Unorganised Workers",
    "cat": "employment",
    "desc": "National database of unorganised workers. Register to get UAN universal account number. Rs 2 lakh accident insurance through PM Suraksha Bima. Priority for social security schemes and welfare measures.",
    "eligibility": "Unorganised sector workers aged 16-59, not EPFO/ESIC member",
    "ministry": "Labour & Employment",
    "benefit": "Rs 2 Lakh accident cover + priority welfare",
    "age_min": 16, "age_max": 59,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 500000,
    "occupation": ["Farmer","Daily Wage Worker","Self-employed"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "e-SHRAM unorganised worker registration UAN labour insurance database"
  },
  {
    "id": 30, "name": "PM Vishwakarma",
    "full": "PM Vishwakarma Yojana",
    "cat": "employment",
    "desc": "Support scheme for artisans craftspeople and traditional workers. Collateral free loans at 5 percent interest. Skills training with stipend. Modern tools and technology support. Covers 18 traditional trades including carpenter blacksmith weaver potter goldsmith.",
    "eligibility": "Artisans and craftspeople from 18 traditional trades",
    "ministry": "MSME",
    "benefit": "Loans at 5% + free skill training + tools",
    "age_min": 18, "age_max": 70,
    "gender": ["Male","Female","Transgender"],
    "category": ["General","OBC","SC","ST","EWS"],
    "income_max": 999999,
    "occupation": ["Self-employed","Farmer"],
    "residence": ["Rural","Urban","Semi-Urban"],
    "bpl_required": False,
    "link": "",
    "tags": "artisan craftsman traditional trade vishwakarma carpenter weaver potter loan skill"
  },
]

print(f"✅ Loaded {len(SCHEMES)} government schemes")

# ─────────────────────────────────────────────────────────────────
# 2. TRAIN SEARCH MODEL  (TF-IDF + Cosine Similarity)
# ─────────────────────────────────────────────────────────────────
print("\n📚 Training Search Model (TF-IDF)...")

# Build rich text corpus for each scheme
def build_corpus(s):
    return f"{s['full']} {s['name']} {s['desc']} {s['eligibility']} {s['tags']} {s['cat']} {s['benefit']}"

corpus = [build_corpus(s) for s in SCHEMES]

search_vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words='english',
    sublinear_tf=True,
    min_df=1
)
tfidf_matrix = search_vectorizer.fit_transform(corpus)

print(f"   TF-IDF Matrix: {tfidf_matrix.shape}")
print("   ✅ Search model ready")

# ─────────────────────────────────────────────────────────────────
# 3. TRAIN ELIGIBILITY MODEL  (Random Forest)
# ─────────────────────────────────────────────────────────────────
print("\n🌲 Training Eligibility Model (Random Forest)...")

# Encode categorical variables
income_map = {
    "below 50000": 25000,
    "50000 to 1 lakh": 75000,
    "1 to 2.5 lakh": 175000,
    "2.5 to 5 lakh": 375000,
    "above 5 lakh": 750000,
    "0": 0
}
gender_map = {"Male": 0, "Female": 1, "Transgender": 2}
category_map = {"General": 0, "OBC": 1, "SC": 2, "ST": 3, "EWS": 4}
occupation_map = {
    "Farmer": 0, "Daily Wage Worker": 1, "Student": 2,
    "Unemployed": 3, "Self-employed": 4, "Salaried": 5,
    "Senior Citizen": 6, "Differently Abled": 7
}
residence_map = {"Rural": 0, "Urban": 1, "Semi-Urban": 2}
marital_map = {"Single": 0, "Married": 1, "Widowed": 2, "Divorced": 3}
edu_map = {
    "No Formal Education": 0, "Primary (1-5)": 1, "Secondary (6-10)": 2,
    "Higher Secondary (11-12)": 3, "Graduate": 4, "Post Graduate": 5
}

# Generate synthetic training data
np.random.seed(42)
training_rows = []

for _ in range(5000):
    age = np.random.randint(1, 90)
    gender = np.random.choice(["Male", "Female", "Transgender"], p=[0.49, 0.49, 0.02])
    cat = np.random.choice(["General", "OBC", "SC", "ST", "EWS"], p=[0.25, 0.3, 0.2, 0.15, 0.1])
    income_key = np.random.choice(list(income_map.keys())[:-1])
    income = income_map[income_key]
    occ = np.random.choice(list(occupation_map.keys()))
    res = np.random.choice(["Rural", "Urban", "Semi-Urban"], p=[0.65, 0.25, 0.1])
    bpl = np.random.choice([True, False], p=[0.4, 0.6])
    marital = np.random.choice(["Single", "Married", "Widowed", "Divorced"], p=[0.3, 0.55, 0.1, 0.05])
    edu = np.random.choice(list(edu_map.keys()))

    eligible_ids = []
    for s in SCHEMES:
        if age < s["age_min"] or age > s["age_max"]:
            continue
        if gender not in s["gender"]:
            continue
        if cat not in s["category"]:
            continue
        if income > s["income_max"]:
            continue
        if occ not in s["occupation"]:
            continue
        if res not in s["residence"]:
            continue
        if s["bpl_required"] and not bpl:
            continue
        eligible_ids.append(s["id"])

    training_rows.append({
        "age": age,
        "gender": gender_map.get(gender, 0),
        "category": category_map.get(cat, 0),
        "income": income,
        "occupation": occupation_map.get(occ, 3),
        "residence": residence_map.get(res, 0),
        "bpl": int(bpl),
        "marital": marital_map.get(marital, 0),
        "education": edu_map.get(edu, 0),
        "eligible_ids": eligible_ids
    })

df = pd.DataFrame(training_rows)
print(f"   Training samples: {len(df)}")

# Prepare X
X = df[["age", "gender", "category", "income", "occupation", "residence", "bpl", "marital", "education"]].values

# Prepare Y (multi-label: one column per scheme)
scheme_ids = [s["id"] for s in SCHEMES]
Y = np.zeros((len(df), len(scheme_ids)), dtype=int)
for i, row in enumerate(training_rows):
    for sid in row["eligible_ids"]:
        j = scheme_ids.index(sid)
        Y[i, j] = 1

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

elig_model = MultiOutputClassifier(
    RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
)
elig_model.fit(X_train, Y_train)

# Evaluate
Y_pred = elig_model.predict(X_test)
accuracy_per_label = (Y_pred == Y_test).mean(axis=0)
print(f"   Mean label accuracy: {accuracy_per_label.mean():.3f}")
print("   ✅ Eligibility model trained")

# ─────────────────────────────────────────────────────────────────
# 4. TRAIN CHATBOT INTENT MODEL
# ─────────────────────────────────────────────────────────────────
print("\n💬 Training Chatbot Intent Classifier...")

intent_data = [
    # search_scheme
    ("what schemes are available for farmers", "search_scheme"),
    ("tell me about government schemes for poor people", "search_scheme"),
    ("which scheme gives money to farmers", "search_scheme"),
    ("schemes related to health", "search_scheme"),
    ("education scholarship for SC students", "search_scheme"),
    ("housing scheme for BPL", "search_scheme"),
    ("employment scheme rural area", "search_scheme"),
    ("women welfare scheme", "search_scheme"),
    ("list of all government schemes", "search_scheme"),
    ("scheme for girl child", "search_scheme"),
    ("scheme for senior citizens", "search_scheme"),
    ("disability pension scheme", "search_scheme"),
    ("crop insurance scheme", "search_scheme"),
    ("skill training scheme for youth", "search_scheme"),
    ("food ration scheme poor families", "search_scheme"),
    ("water connection rural scheme", "search_scheme"),
    ("loan scheme for small business", "search_scheme"),
    # explain_scheme
    ("explain PM Kisan yojana", "explain_scheme"),
    ("what is Ayushman Bharat", "explain_scheme"),
    ("tell me about MGNREGA", "explain_scheme"),
    ("how does ujjwala yojana work", "explain_scheme"),
    ("describe PMAY housing scheme", "explain_scheme"),
    ("what is Sukanya Samriddhi Yojana", "explain_scheme"),
    ("explain MUDRA loan scheme", "explain_scheme"),
    ("what is beti bachao beti padhao", "explain_scheme"),
    ("tell me about atal pension yojana", "explain_scheme"),
    ("what is PM SVANidhi scheme", "explain_scheme"),
    # how_to_apply
    ("how to apply for PM Kisan", "how_to_apply"),
    ("where to register for Ayushman Bharat", "how_to_apply"),
    ("what is the process to get MGNREGA job card", "how_to_apply"),
    ("how to enroll in ujjwala yojana", "how_to_apply"),
    ("application process for scholarship", "how_to_apply"),
    ("how to get ration card", "how_to_apply"),
    ("where to apply for PMAY house", "how_to_apply"),
    ("registration steps for PM Kaushal Vikas", "how_to_apply"),
    ("how to open Jan Dhan account", "how_to_apply"),
    # documents_needed
    ("what documents needed for PM Kisan", "documents_needed"),
    ("documents required for Ayushman card", "documents_needed"),
    ("which papers to submit for MGNREGA", "documents_needed"),
    ("documents for scholarship application", "documents_needed"),
    ("what proof needed for ration card", "documents_needed"),
    ("documents for PMAY application", "documents_needed"),
    ("aadhar required for which schemes", "documents_needed"),
    ("income certificate needed for which scheme", "documents_needed"),
    # check_eligibility
    ("am I eligible for PM Kisan", "check_eligibility"),
    ("can I get Ayushman Bharat card", "check_eligibility"),
    ("who can apply for MGNREGA", "check_eligibility"),
    ("am I eligible for scholarship", "check_eligibility"),
    ("can poor people get housing scheme", "check_eligibility"),
    ("eligibility criteria for MUDRA loan", "check_eligibility"),
    ("who qualifies for old age pension", "check_eligibility"),
    ("can widow apply for pension", "check_eligibility"),
    # greeting
    ("hello", "greeting"),
    ("hi there", "greeting"),
    ("namaste", "greeting"),
    ("good morning", "greeting"),
    ("help me", "greeting"),
    ("what can you do", "greeting"),
    ("how can you help me", "greeting"),
]

intent_texts = [d[0] for d in intent_data]
intent_labels = [d[1] for d in intent_data]

intent_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
X_intent = intent_vectorizer.fit_transform(intent_texts)

intent_le = LabelEncoder()
Y_intent = intent_le.fit_transform(intent_labels)

intent_clf = RandomForestClassifier(n_estimators=100, random_state=42)
intent_clf.fit(X_intent, Y_intent)
print(f"   Intent classes: {list(intent_le.classes_)}")
print("   ✅ Chatbot intent model trained")

# ─────────────────────────────────────────────────────────────────
# 5. SAVE ALL MODELS
# ─────────────────────────────────────────────────────────────────
print("\n💾 Saving models...")

os.makedirs("models", exist_ok=True)

with open("models/search_vectorizer.pkl", "wb") as f:
    pickle.dump(search_vectorizer, f)
with open("models/tfidf_matrix.pkl", "wb") as f:
    pickle.dump(tfidf_matrix, f)
with open("models/schemes.pkl", "wb") as f:
    pickle.dump(SCHEMES, f)
with open("models/elig_model.pkl", "wb") as f:
    pickle.dump(elig_model, f)
with open("models/intent_vectorizer.pkl", "wb") as f:
    pickle.dump(intent_vectorizer, f)
with open("models/intent_clf.pkl", "wb") as f:
    pickle.dump(intent_clf, f)
with open("models/intent_le.pkl", "wb") as f:
    pickle.dump(intent_le, f)

# Save encoding maps
encoding_maps = {
    "income_map": income_map,
    "gender_map": gender_map,
    "category_map": category_map,
    "occupation_map": occupation_map,
    "residence_map": residence_map,
    "marital_map": marital_map,
    "edu_map": edu_map,
    "scheme_ids": scheme_ids
}
with open("models/encoding_maps.pkl", "wb") as f:
    pickle.dump(encoding_maps, f)

print("   ✅ All models saved in /models/")

print("\n" + "="*60)
print("✅  TRAINING COMPLETE!")
print("="*60)
print(f"   Search model  → TF-IDF on {len(SCHEMES)} schemes")
print(f"   Eligibility   → Random Forest, {len(training_rows)} samples")
print(f"   Chat intent   → {len(intent_data)} training examples")
print("\n▶  Now run: python app.py")
