#!/usr/bin/env python3
"""
ISCOL 2025 Registration Outliers and Interesting Findings
This script identifies unusual, interesting, and outlier registrations.
"""

import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)


def find_outliers(csv_file):
    """Find interesting outliers and unusual patterns in the registration data."""

    df = pd.read_csv(csv_file)

    print("=" * 80)
    print("🔍 ISCOL 2025 REGISTRATION OUTLIERS & INTERESTING FINDINGS 🔍")
    print("=" * 80)
    print()

    # ========================================================================
    # 1. EMAIL ANOMALIES
    # ========================================================================
    print("=" * 80)
    print("📧 EMAIL ANOMALIES")
    print("=" * 80)

    # Invalid or unusual emails
    invalid_emails = []
    unusual_emails = []

    for idx, row in df.iterrows():
        email = str(row['Email Address']).strip()

        # Check for completely invalid emails
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            if email not in ['nan', '']:
                invalid_emails.append({
                    'email': email,
                    'name': row['Full Name'],
                    'affiliation': row['Affiliation (University/Company)']
                })

        # Check for unusual patterns
        elif any(char in email for char in ['..', '--', '__']):
            unusual_emails.append(email)

    if invalid_emails:
        print(f"\n🚨 Found {len(invalid_emails)} INVALID email(s):")
        for item in invalid_emails:
            print(f"  • {item['name']}: {item['email']}")
            print(f"    Affiliation: {item['affiliation']}")

    # Check for phone numbers in affiliation field
    print("\n📱 PHONE NUMBERS in Affiliation Field:")
    phone_pattern = r'\d{10}|\d{3}-\d{3}-\d{4}'
    phone_affiliations = df[df['Affiliation (University/Company)'].astype(str).str.match(r'^\d+$')]
    if len(phone_affiliations) > 0:
        for idx, row in phone_affiliations.iterrows():
            print(f"  • {row['Full Name']}: {row['Affiliation (University/Company)']}")

    # ========================================================================
    # 2. DUPLICATE PEOPLE (Same email, multiple registrations)
    # ========================================================================
    print("\n" + "=" * 80)
    print("👥 DUPLICATE REGISTRATIONS (Same Person, Multiple Times)")
    print("=" * 80)

    email_counts = df['Email Address'].value_counts()
    duplicates = email_counts[email_counts > 1]

    if len(duplicates) > 0:
        print(f"\nFound {len(duplicates)} people who registered multiple times:")
        for email, count in duplicates.head(10).items():
            person_records = df[df['Email Address'] == email]
            print(f"\n  📬 {email} ({count} registrations):")
            for idx, row in person_records.iterrows():
                print(f"     • {row['Timestamp']} - {row['Full Name']}")
                print(f"       Attending: {row['Are you attending ISCOL 2025?']}")

    # ========================================================================
    # 3. NAME VARIATIONS (Similar names, different emails)
    # ========================================================================
    print("\n" + "=" * 80)
    print("🔤 POTENTIAL NAME VARIATIONS")
    print("=" * 80)

    # Group by similar names
    name_dict = {}
    for idx, row in df.iterrows():
        name = str(row['Full Name']).lower().strip()
        name_key = re.sub(r'[^\w]', '', name)  # Remove special chars
        if name_key not in name_dict:
            name_dict[name_key] = []
        name_dict[name_key].append({
            'original_name': row['Full Name'],
            'email': row['Email Address'],
            'affiliation': row['Affiliation (University/Company)']
        })

    # Find potential duplicates
    potential_dupes = {k: v for k, v in name_dict.items() if len(v) > 1}
    if potential_dupes:
        print(f"\nFound {len(potential_dupes)} potential duplicate names:")
        for name_key, records in list(potential_dupes.items())[:5]:
            if len(records) > 1:
                print(f"\n  • Variations:")
                for rec in records:
                    print(f"    - {rec['original_name']} ({rec['email']})")

    # ========================================================================
    # 4. GEOGRAPHICAL OUTLIERS (International attendees)
    # ========================================================================
    print("\n" + "=" * 80)
    print("🌍 INTERNATIONAL & REMOTE ATTENDEES")
    print("=" * 80)

    international_keywords = ['harvard', 'stanford', 'miami', 'zurich', 'upenn', 'pennsylvania',
                             'mcgill', 'mila', 'usf', 'south florida', 'kempner']

    international = []
    for idx, row in df.iterrows():
        affiliation = str(row['Affiliation (University/Company)']).lower()
        if any(keyword in affiliation for keyword in international_keywords):
            international.append({
                'name': row['Full Name'],
                'affiliation': row['Affiliation (University/Company)'],
                'attending': row['Are you attending ISCOL 2025?'],
                'email': row['Email Address']
            })

    if international:
        print(f"\n🛫 {len(international)} International attendees detected:")
        for person in international:
            status = "✅" if person['attending'] == 'Yes' else "❓" if person['attending'] == 'Maybe, not sure yet' else "❌"
            print(f"  {status} {person['name']}")
            print(f"      From: {person['affiliation']}")

    # ========================================================================
    # 5. ROLE OUTLIERS (Unique/Unusual Roles)
    # ========================================================================
    print("\n" + "=" * 80)
    print("🎭 UNIQUE & INTERESTING ROLES")
    print("=" * 80)

    role_counts = df['I identify as a:'].value_counts()
    rare_roles = role_counts[role_counts == 1]

    print(f"\n🌟 {len(rare_roles)} One-of-a-kind roles:")
    interesting_roles = []
    for role in rare_roles.index:
        if pd.notna(role) and role not in ['Graduate student', 'Industry researcher', 'Faculty member']:
            person = df[df['I identify as a:'] == role].iloc[0]
            interesting_roles.append({
                'role': role,
                'name': person['Full Name'],
                'affiliation': person['Affiliation (University/Company)']
            })

    for item in sorted(interesting_roles, key=lambda x: len(x['role']), reverse=True)[:15]:
        print(f"  • '{item['role']}'")
        print(f"    → {item['name']} from {item['affiliation']}")

    # ========================================================================
    # 6. EARLY BIRDS & LATE ARRIVALS
    # ========================================================================
    print("\n" + "=" * 80)
    print("⏰ REGISTRATION TIMING OUTLIERS")
    print("=" * 80)

    df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df_valid_time = df[df['Timestamp_dt'].notna()].copy()

    if len(df_valid_time) > 0:
        # First 5 registrations
        earliest = df_valid_time.nsmallest(5, 'Timestamp_dt')
        print("\n🐦 FIRST 5 EARLY BIRDS:")
        for idx, row in earliest.iterrows():
            print(f"  {row['Timestamp_dt'].strftime('%Y-%m-%d %H:%M')} - {row['Full Name']}")
            print(f"    {row['Affiliation (University/Company)']}")

        # Last 5 registrations
        latest = df_valid_time.nlargest(5, 'Timestamp_dt')
        print("\n⏰ LAST 5 LAST-MINUTE REGISTRATIONS:")
        for idx, row in latest.iterrows():
            print(f"  {row['Timestamp_dt'].strftime('%Y-%m-%d %H:%M')} - {row['Full Name']}")
            print(f"    {row['Affiliation (University/Company)']}")

        # Weekend registrations
        df_valid_time['day_of_week'] = df_valid_time['Timestamp_dt'].dt.day_name()
        weekend_regs = df_valid_time[df_valid_time['day_of_week'].isin(['Saturday', 'Sunday'])]
        print(f"\n📅 Weekend Warriors: {len(weekend_regs)} registrations on weekends")

        # Late night registrations (after 10 PM or before 6 AM)
        df_valid_time['hour'] = df_valid_time['Timestamp_dt'].dt.hour
        night_owls = df_valid_time[(df_valid_time['hour'] >= 22) | (df_valid_time['hour'] < 6)]
        if len(night_owls) > 0:
            print(f"\n🦉 Night Owls: {len(night_owls)} registrations between 10 PM - 6 AM")
            print("    Most dedicated:")
            for idx, row in night_owls.nsmallest(3, 'hour').iterrows():
                hour = row['Timestamp_dt'].strftime('%I:%M %p')
                print(f"    • {row['Full Name']} at {hour}")

    # ========================================================================
    # 7. COMMENT OUTLIERS (Interesting comments)
    # ========================================================================
    print("\n" + "=" * 80)
    print("💬 INTERESTING COMMENTS & REQUESTS")
    print("=" * 80)

    comments = df[df['Any additional comments or requests?'].notna() &
                  (df['Any additional comments or requests?'] != '')]

    print(f"\n📝 {len(comments)} people left comments. Here are some interesting ones:")

    # Categorize comments
    funny_keywords = ['peace', 'thanks', 'excited', 'looking forward', 'אתה', 'מלך']
    requests = []
    appreciation = []
    special = []

    for idx, row in comments.iterrows():
        comment = str(row['Any additional comments or requests?'])
        name = row['Full Name']

        if any(word in comment.lower() for word in ['thank', 'great', 'excited', 'looking forward', 'מלך']):
            appreciation.append((name, comment))
        elif any(word in comment.lower() for word in ['poster', 'session', 'flight', 'park', 'veg']):
            requests.append((name, comment))
        elif len(comment) > 50:
            special.append((name, comment))

    if appreciation:
        print("\n💖 APPRECIATION & ENTHUSIASM:")
        for name, comment in appreciation[:5]:
            print(f"  • {name}: \"{comment}\"")

    if requests:
        print("\n📋 SPECIAL REQUESTS:")
        for name, comment in requests[:5]:
            print(f"  • {name}: \"{comment}\"")

    # ========================================================================
    # 8. AFFILIATION OUTLIERS
    # ========================================================================
    print("\n" + "=" * 80)
    print("🏢 UNUSUAL AFFILIATIONS")
    print("=" * 80)

    # Single character or very short affiliations
    short_affiliations = df[df['Affiliation (University/Company)'].astype(str).str.len() < 3]
    if len(short_affiliations) > 0:
        print(f"\n🤔 Suspiciously short affiliations ({len(short_affiliations)}):")
        for idx, row in short_affiliations.head(10).iterrows():
            print(f"  • {row['Full Name']}: '{row['Affiliation (University/Company)']}' (attending: {row['Are you attending ISCOL 2025?']})")

    # Unique/rare affiliations
    affiliation_counts = df['Affiliation (University/Company)'].value_counts()
    unique_affiliations = affiliation_counts[affiliation_counts == 1]

    interesting_unique = []
    common_words = ['university', 'college', 'institute', 'research', 'lab', 'ai', 'tech']

    for affiliation in unique_affiliations.index:
        if pd.notna(affiliation):
            aff_lower = str(affiliation).lower()
            if not any(word in aff_lower for word in common_words) and len(str(affiliation)) > 3:
                person = df[df['Affiliation (University/Company)'] == affiliation].iloc[0]
                if person['Are you attending ISCOL 2025?'] == 'Yes':
                    interesting_unique.append({
                        'affiliation': affiliation,
                        'name': person['Full Name']
                    })

    if interesting_unique:
        print(f"\n🦄 Unique/Interesting companies (attending):")
        for item in interesting_unique[:10]:
            print(f"  • {item['name']} from '{item['affiliation']}'")

    # ========================================================================
    # 9. STATISTICAL OUTLIERS
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 STATISTICAL PATTERNS & ODDITIES")
    print("=" * 80)

    # People who said "Maybe" to everything
    maybes = df[
        (df['Are you attending ISCOL 2025?'] == 'Maybe, not sure yet') &
        (df['Will you be driving a car?'] == 'Maybe, not sure yet')
    ]
    if len(maybes) > 0:
        print(f"\n🤷 The Indecisive Club - {len(maybes)} people who selected 'Maybe' for multiple questions:")
        for idx, row in maybes.head(5).iterrows():
            print(f"  • {row['Full Name']} ({row['Affiliation (University/Company)']})")

    # People with empty role but attending
    no_role_attending = df[
        (df['I identify as a:'].isna() | (df['I identify as a:'] == '')) &
        (df['Are you attending ISCOL 2025?'] == 'Yes')
    ]
    if len(no_role_attending) > 0:
        print(f"\n🎭 Mystery Guests - {len(no_role_attending)} attendees without specified role:")
        for idx, row in no_role_attending.iterrows():
            print(f"  • {row['Full Name']} from {row['Affiliation (University/Company)']}")

    # Submitting paper but not attending
    paper_not_attending = df[
        (df['Did you submit a paper to ISCOL?'] == 'Yes') &
        (df['Are you attending ISCOL 2025?'] == 'No')
    ]
    if len(paper_not_attending) > 0:
        print(f"\n📄 Paper Submitters Not Attending - {len(paper_not_attending)} submitted papers but won't attend:")
        for idx, row in paper_not_attending.iterrows():
            print(f"  • {row['Full Name']} ({row['Affiliation (University/Company)']})")

    # ========================================================================
    # 10. VISUALIZATION OF OUTLIERS
    # ========================================================================
    print("\n" + "=" * 80)
    print("📈 GENERATING OUTLIER VISUALIZATIONS")
    print("=" * 80)

    fig = plt.figure(figsize=(18, 12))

    # 1. Registration by hour of day
    if len(df_valid_time) > 0:
        ax1 = plt.subplot(2, 3, 1)
        hour_dist = df_valid_time['hour'].value_counts().sort_index()
        ax1.bar(hour_dist.index, hour_dist.values, color='skyblue', edgecolor='navy')
        ax1.axvspan(22, 24, alpha=0.3, color='purple', label='Night Owls (10PM-6AM)')
        ax1.axvspan(0, 6, alpha=0.3, color='purple')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Number of Registrations')
        ax1.set_title('🦉 Registration by Hour (Night Owls Highlighted)', fontweight='bold')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

    # 2. Duplicate registrations
    ax2 = plt.subplot(2, 3, 2)
    if len(duplicates) > 0:
        top_dupes = duplicates.head(10).sort_values()
        ax2.barh(range(len(top_dupes)), top_dupes.values, color='salmon', edgecolor='darkred')
        ax2.set_yticks(range(len(top_dupes)))
        ax2.set_yticklabels([email[:20] + '...' if len(email) > 20 else email
                             for email in top_dupes.index], fontsize=8)
        ax2.set_xlabel('Number of Registrations')
        ax2.set_title('👥 Top Duplicate Registrations', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)

    # 3. Comment length distribution
    ax3 = plt.subplot(2, 3, 3)
    comment_lengths = comments['Any additional comments or requests?'].str.len()
    ax3.hist(comment_lengths, bins=30, color='lightgreen', edgecolor='darkgreen')
    ax3.axvline(comment_lengths.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {comment_lengths.mean():.0f}')
    ax3.set_xlabel('Comment Length (characters)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('💬 Comment Length Distribution', fontweight='bold')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)

    # 4. Registration timeline with outliers
    ax4 = plt.subplot(2, 3, 4)
    if len(df_valid_time) > 0:
        df_valid_time['date_only'] = df_valid_time['Timestamp_dt'].dt.date
        daily_regs = df_valid_time['date_only'].value_counts().sort_index()
        ax4.plot(daily_regs.index, daily_regs.values, marker='o', linewidth=2, markersize=4)
        # Highlight outlier days
        mean_regs = daily_regs.mean()
        std_regs = daily_regs.std()
        outlier_days = daily_regs[daily_regs > mean_regs + 1.5 * std_regs]
        if len(outlier_days) > 0:
            ax4.scatter(outlier_days.index, outlier_days.values,
                       color='red', s=100, zorder=5, label='High Activity Days')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Registrations')
        ax4.set_title('📅 Registration Timeline (Spikes Highlighted)', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # 5. Affiliation name length
    ax5 = plt.subplot(2, 3, 5)
    aff_lengths = df['Affiliation (University/Company)'].astype(str).str.len()
    ax5.hist(aff_lengths, bins=40, color='plum', edgecolor='purple')
    # Highlight outliers
    q1, q3 = aff_lengths.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower_outliers = aff_lengths[aff_lengths < q1 - 1.5 * iqr]
    upper_outliers = aff_lengths[aff_lengths > q3 + 1.5 * iqr]
    if len(lower_outliers) > 0:
        ax5.axvline(q1 - 1.5 * iqr, color='red', linestyle='--', linewidth=2, label='Outlier Threshold')
    if len(upper_outliers) > 0:
        ax5.axvline(q3 + 1.5 * iqr, color='red', linestyle='--', linewidth=2)
    ax5.set_xlabel('Affiliation Name Length')
    ax5.set_ylabel('Frequency')
    ax5.set_title('🏢 Affiliation Name Length (Outliers Marked)', fontweight='bold')
    if len(lower_outliers) > 0 or len(upper_outliers) > 0:
        ax5.legend()
    ax5.grid(axis='y', alpha=0.3)

    # 6. Decision patterns
    ax6 = plt.subplot(2, 3, 6)
    decision_data = {
        'Attending:\nYes': len(df[df['Are you attending ISCOL 2025?'] == 'Yes']),
        'Attending:\nMaybe': len(df[df['Are you attending ISCOL 2025?'] == 'Maybe, not sure yet']),
        'Attending:\nNo': len(df[df['Are you attending ISCOL 2025?'] == 'No']),
        'Driving:\nMaybe': len(df[df['Will you be driving a car?'] == 'Maybe, not sure yet']),
    }
    colors_decision = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
    ax6.bar(decision_data.keys(), decision_data.values(), color=colors_decision, edgecolor='black')
    ax6.set_ylabel('Count')
    ax6.set_title('🤷 Decision Patterns & Uncertainty', fontweight='bold')
    ax6.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_plot = csv_file.replace('.csv', '_outliers.png')
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"\n✅ Outlier visualization saved to: {output_plot}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("🎯 OUTLIER SUMMARY")
    print("=" * 80)
    print(f"• Invalid emails: {len(invalid_emails)}")
    print(f"• Duplicate registrations: {len(duplicates)}")
    print(f"• International attendees: {len(international)}")
    print(f"• Unique roles: {len(rare_roles)}")
    print(f"• Weekend registrations: {len(weekend_regs) if len(df_valid_time) > 0 else 0}")
    print(f"• Night owl registrations: {len(night_owls) if len(df_valid_time) > 0 else 0}")
    print(f"• People with comments: {len(comments)}")
    print(f"• Mystery guests (no role): {len(no_role_attending)}")
    print("=" * 80)
    print()


if __name__ == '__main__':
    find_outliers('iscol-registration.csv')
