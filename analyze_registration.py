#!/usr/bin/env python3
"""
ISCOL 2025 Registration Data Analysis Script
This script cleans and analyzes the ISCOL registration CSV file.
"""

import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def normalize_company_name(company):
    """Normalize company/affiliation names to handle variations.
    Returns a list of affiliations to handle multiple affiliations."""
    if pd.isna(company) or company == '-':
        return ['Not specified']

    # Convert to string and lowercase for comparison
    company = str(company).strip().lower()

    # Check if it looks like an email address - if so, extract domain for matching
    if '@' in company and re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', company):
        # Extract domain from email
        domain = company.split('@')[1]
        company = domain  # Use domain for matching instead

    # Mapping of variations to canonical names
    mappings = {
        'ai2': ['ai2'],
        'AI21': ['ai21', 'ai21 labs'],
        'Amazon': ['amazon'],
        'Ariel University': ['ariel', 'ariel university'],
        'Bar Ilan University': ['bar ilan', 'bar-ilan', 'biu', 'bar ilan university', 'bar-ilan university',
                                'bar illan university', 'bar ilan /'],
        'Ben Gurion University': ['ben gurion', 'ben-gurion', 'bgu', 'ben gurion university',
                                  'ben-gurion university', 'ben gurion university of the negev'],
        'Bold': ['bold', 'bold.ai', 'bold ai'],
        'Dicta': ['dicta', 'dicta: israel center for text analysis'],
        'GE Healthcare': ['ge healthcare', 'ge health'],
        'Genesys': ['genesys'],
        'Gong': ['gong', 'gong io', 'gong.io'],
        'Google': ['google', 'google research'],
        'Hebrew University': ['hebrew university', 'huji', 'the hebrew university',
                             'the hebrew university of jerusalem', 'hebrew university of jerusalem'],
        'IBM': ['ibm', 'ibm r', 'ibm research', 'ibm resaerch', 'ibm research - isrl'],
        'IDF': ['idf'],
        'Intel': ['intel'],
        'Microsoft': ['microsoft'],
        'Nexxen': ['nexxen'],
        'OriginAI': ['originai'],
        'Reichman University': ['reichman', 'reichman university', 'reichmann university'],
        'Rival Security': ['rival security', 'rival'],
        'Salesforce': ['salesforce', 'salesforce.com'],
        'Second Nature': ['second nature', 'second nature ai'],
        'Sheba AI Center': ['sheba', 'sheba ai center', 'sheba medical center', 'arc sheba ai center'],
        'Technion': ['technion', 'technion - israel institute of technology',
                    'technion- israel institute for technology'],
        'Tel Aviv University': ['tau', 'tel aviv university', 'tel aviv university '],
        'Walmart': ['walmart', 'walmart (aspectiva)', 'walmart aspectiva'],
        'Weizmann Institute': ['weizmann', 'weizmann institute', 'weizmann institute of science'],
        'Wix': ['wix', 'wix.com'],
    }

    # Check if there are multiple affiliations separated by common delimiters
    # Common separators: comma, slash, "and"
    potential_parts = []
    for sep in [',', '/', ' and ', '&']:
        if sep in company:
            potential_parts = [part.strip() for part in company.split(sep)]
            break

    if not potential_parts:
        potential_parts = [company]

    # Normalize each part
    normalized = []
    for part in potential_parts:
        part = part.strip()
        if not part:
            continue

        # Try to match with mappings
        matched = False
        for canonical, variations in mappings.items():
            for variation in variations:
                if variation in part or part in variation:
                    if canonical not in normalized:
                        normalized.append(canonical)
                    matched = True
                    break
            if matched:
                break

        if not matched:
            # Return original (title case) if no mapping found
            normalized.append(part.title())

    return normalized if normalized else ['Not specified']


def clean_email(email):
    """Clean and validate email addresses."""
    if pd.isna(email):
        return None
    email = str(email).strip().lower()
    # Simple email validation
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return email
    return None


def analyze_registration_data(csv_file):
    """Main function to clean and analyze registration data."""

    print("=" * 80)
    print("ISCOL 2025 REGISTRATION DATA ANALYSIS")
    print("=" * 80)
    print()

    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"Total records loaded: {len(df)}")
    print()

    # Clean email addresses
    df['Email Address'] = df['Email Address'].apply(clean_email)

    # Remove duplicates based on email (keeping first occurrence)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['Email Address'], keep='first')
    duplicates_removed = initial_count - len(df)
    print(f"Duplicates removed (by email): {duplicates_removed}")
    print(f"Unique registrations: {len(df)}")
    print()

    # Normalize company names (returns lists)
    df['Affiliation_Normalized'] = df['Affiliation (University/Company)'].apply(normalize_company_name)

    # Clean up attendance column
    df['Attending'] = df['Are you attending ISCOL 2025?'].fillna('Not specified')

    # Clean up role column
    df['Role'] = df['I identify as a:'].fillna('Not specified')

    # Clean up paper submission column
    df['Submitted_Paper'] = df['Did you submit a paper to ISCOL?'].fillna('Not specified')

    # Clean up driving column
    df['Driving'] = df['Will you be driving a car?'].fillna('Not specified')

    print("=" * 80)
    print("DATA CLEANING SUMMARY")
    print("=" * 80)
    print(f"Total unique participants: {len(df)}")
    print(f"Records with valid email: {df['Email Address'].notna().sum()}")
    # Count records with at least one non-"Not specified" affiliation
    has_affiliation = df['Affiliation_Normalized'].apply(
        lambda x: len(x) > 0 and not (len(x) == 1 and x[0] == 'Not specified')
    ).sum()
    print(f"Records with affiliation: {has_affiliation}")
    print()

    # === ATTENDANCE ANALYSIS ===
    print("=" * 80)
    print("ATTENDANCE STATUS")
    print("=" * 80)
    attendance_counts = df['Attending'].value_counts()
    print(attendance_counts)
    print()
    yes_count = attendance_counts.get('Yes', 0)
    print(f"Expected attendees: {yes_count} ({yes_count/len(df)*100:.1f}%)")
    print()

    # Filter for confirmed attendees for remaining analyses
    df_attending = df[df['Attending'] == 'Yes'].copy()

    # === AFFILIATION ANALYSIS ===
    print("=" * 80)
    print("TOP 20 AFFILIATIONS (Confirmed Attendees)")
    print("=" * 80)
    # Explode the list of affiliations so each person can be counted for multiple orgs
    df_attending_exploded = df_attending.explode('Affiliation_Normalized')
    affiliation_counts = df_attending_exploded['Affiliation_Normalized'].value_counts().head(20)
    for i, (affiliation, count) in enumerate(affiliation_counts.items(), 1):
        print(f"{i:2d}. {affiliation:40s} : {count:3d} attendees")
    print()

    # === ROLE ANALYSIS ===
    print("=" * 80)
    print("PARTICIPANT ROLES (Confirmed Attendees)")
    print("=" * 80)
    role_counts = df_attending['Role'].value_counts()
    for role, count in role_counts.items():
        percentage = count / len(df_attending) * 100
        print(f"  {role:40s} : {count:3d} ({percentage:5.1f}%)")
    print()

    # Categorize roles
    academic_roles = ['Graduate student', 'Student (BA/BSc)', 'Faculty member', 'PhD student',
                     'PhD Student', 'Post-doc', 'MSc student', 'M.Sc. Student', 'MSc Graduate',
                     'Msc student', 'MSc Student in CS', 'M.S.c Student', 'MS Student']
    industry_roles = ['Industry researcher', 'Industry engineer', 'Industry member',
                     'Data Executive', 'Principal Engineering Lead', 'Product Manager',
                     'Industry NLP Product Manager']

    academic_count = df_attending[df_attending['Role'].isin(academic_roles)].shape[0]
    industry_count = df_attending[df_attending['Role'].isin(industry_roles)].shape[0]
    other_count = len(df_attending) - academic_count - industry_count

    print("Role Categories:")
    print(f"  Academic: {academic_count} ({academic_count/len(df_attending)*100:.1f}%)")
    print(f"  Industry: {industry_count} ({industry_count/len(df_attending)*100:.1f}%)")
    print(f"  Other:    {other_count} ({other_count/len(df_attending)*100:.1f}%)")
    print()

    # === PAPER SUBMISSIONS ===
    print("=" * 80)
    print("PAPER SUBMISSIONS (Confirmed Attendees)")
    print("=" * 80)
    paper_counts = df_attending['Submitted_Paper'].value_counts()
    print(paper_counts)
    print()
    yes_papers = paper_counts.get('Yes', 0)
    print(f"Paper submitters: {yes_papers} ({yes_papers/len(df_attending)*100:.1f}% of attendees)")
    print()

    # === DRIVING ANALYSIS ===
    print("=" * 80)
    print("DRIVING STATUS (Confirmed Attendees)")
    print("=" * 80)
    driving_counts = df_attending['Driving'].value_counts()
    print(driving_counts)
    print()

    # === ORGANIZATION TYPE ANALYSIS ===
    print("=" * 80)
    print("ORGANIZATION TYPES (Confirmed Attendees)")
    print("=" * 80)

    # Categorize organizations
    universities = ['Bar Ilan University', 'Ben Gurion University', 'Hebrew University',
                   'Technion', 'Tel Aviv University', 'Weizmann Institute', 'Ariel University',
                   'Reichman University', 'University of Haifa', 'Haifa University']

    companies = ['Google', 'Microsoft', 'IBM', 'Amazon', 'AI21', 'ai2', 'Intel',
                'Salesforce', 'Walmart', 'Gong', 'Wix', 'Bold', 'OriginAI', 'Genesys',
                'Second Nature', 'GE Healthcare', 'Arm', 'Nexxen']

    # Use exploded data to count affiliations (allows double counting for multiple affiliations)
    university_count = df_attending_exploded[df_attending_exploded['Affiliation_Normalized'].isin(universities)].shape[0]
    company_count = df_attending_exploded[df_attending_exploded['Affiliation_Normalized'].isin(companies)].shape[0]
    other_org = df_attending_exploded.shape[0] - university_count - company_count

    print(f"  Universities: {university_count} ({university_count/df_attending_exploded.shape[0]*100:.1f}%)")
    print(f"  Industry:    {company_count} ({company_count/df_attending_exploded.shape[0]*100:.1f}%)")
    print(f"  Other/Mixed:  {other_org} ({other_org/df_attending_exploded.shape[0]*100:.1f}%)")
    print()
    print(f"Note: Counts include multiple affiliations per person, so totals may exceed unique attendee count.")
    print()

    # === REGISTRATION TIMELINE ===
    print("=" * 80)
    print("REGISTRATION TIMELINE")
    print("=" * 80)
    df_attending['Timestamp'] = pd.to_datetime(df_attending['Timestamp'], errors='coerce')
    df_attending['Date'] = df_attending['Timestamp'].dt.date

    registrations_by_date = df_attending['Date'].value_counts().sort_index()
    valid_dates = registrations_by_date[registrations_by_date.index.notna()]
    if len(valid_dates) > 0:
        print(f"First registration: {valid_dates.index[0]}")
        print(f"Last registration:  {valid_dates.index[-1]}")
        print(f"Invalid timestamps: {df_attending['Timestamp'].isna().sum()}")
    print()

    # === SAVE CLEANED DATA ===
    print("=" * 80)
    print("SAVING CLEANED DATA")
    print("=" * 80)

    # Convert affiliation lists to comma-separated strings for CSV output
    df_to_save = df.copy()
    df_to_save['Affiliation_Normalized'] = df_to_save['Affiliation_Normalized'].apply(lambda x: ', '.join(x))

    output_file = csv_file.replace('.csv', '_cleaned.csv')
    df_to_save.to_csv(output_file, index=False)
    print(f"Cleaned data saved to: {output_file}")
    print()

    # === VISUALIZATIONS ===
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)

    base_filename = csv_file.replace('.csv', '')

    # 1. Top affiliations
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    top_10_affiliations = affiliation_counts.head(10)
    top_10_affiliations.plot(kind='barh', ax=ax1, color='steelblue')
    ax1.set_title('Top 10 Affiliations', fontsize=20, fontweight='bold')
    ax1.set_xlabel('Number of Attendees', fontsize=16)
    ax1.tick_params(axis='both', labelsize=14)
    ax1.invert_yaxis()
    plt.tight_layout()
    plot_file_1 = f"{base_filename}_affiliations.png"
    plt.savefig(plot_file_1, dpi=300, bbox_inches='tight')
    print(f"Affiliations visualization saved to: {plot_file_1}")
    plt.close()

    # 2. Role distribution (pie chart)
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    role_data = pd.Series({
        'Academic': academic_count,
        'Industry': industry_count,
        'Other': other_count
    })
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    ax2.pie(role_data, labels=role_data.index, autopct='%1.1f%%', colors=colors, startangle=90,
            textprops={'fontsize': 16})
    ax2.set_title('Participant Roles', fontsize=20, fontweight='bold')
    plt.tight_layout()
    plot_file_2 = f"{base_filename}_roles.png"
    plt.savefig(plot_file_2, dpi=300, bbox_inches='tight')
    print(f"Roles visualization saved to: {plot_file_2}")
    plt.close()

    # 3. Organization types
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    org_data = pd.Series({
        'Universities': university_count,
        'Companies': company_count,
        'Other/Mixed': other_org
    })
    org_data.plot(kind='bar', ax=ax3, color=['#8b9dc3', '#f5a142', '#c9c9c9'])
    ax3.set_title('Organization Types', fontsize=20, fontweight='bold')
    ax3.set_ylabel('Number of Attendees', fontsize=16)
    ax3.tick_params(axis='both', labelsize=14)
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plot_file_3 = f"{base_filename}_organizations.png"
    plt.savefig(plot_file_3, dpi=300, bbox_inches='tight')
    print(f"Organizations visualization saved to: {plot_file_3}")
    plt.close()

    # 4. Paper submissions
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    paper_yes = paper_counts.get('Yes', 0)
    paper_no = paper_counts.get('No', 0)
    paper_data = pd.Series({'Yes': paper_yes, 'No': paper_no})
    paper_data.plot(kind='bar', ax=ax4, color=['#2ecc71', '#e74c3c'])
    ax4.set_title('Paper Submissions', fontsize=20, fontweight='bold')
    ax4.set_ylabel('Number of Attendees', fontsize=16)
    ax4.tick_params(axis='both', labelsize=14)
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=0)
    plt.tight_layout()
    plot_file_4 = f"{base_filename}_papers.png"
    plt.savefig(plot_file_4, dpi=300, bbox_inches='tight')
    print(f"Paper submissions visualization saved to: {plot_file_4}")
    plt.close()
    print()

    # === SUMMARY STATISTICS ===
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total registrations:        {len(df)}")
    print(f"Confirmed attendees:        {yes_count}")
    print(f"Maybe attending:            {attendance_counts.get('Maybe, not sure yet', 0)}")
    print(f"Not attending:              {attendance_counts.get('No', 0)}")
    print(f"Unique affiliations:        {df_attending_exploded['Affiliation_Normalized'].nunique()}")
    print(f"Paper submitters:           {yes_papers}")
    print(f"Driving to event:           {driving_counts.get('Yes', 0)}")
    print(f"Academic participants:      {academic_count}")
    print(f"Industry participants:      {industry_count}")
    print()

    print("=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

    return df


if __name__ == '__main__':
    csv_file = 'iscol-registration.csv'
    df_cleaned = analyze_registration_data(csv_file)
