import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv(r'C:\Users\Yavuz Selim\Desktop\loan_approval_dataset (1).csv')
df.columns = df.columns.str.strip()

cat_cols = ['education', 'self_employed', 'loan_status']
for col in cat_cols:
    df[col] = df[col].str.strip()

# Eksi (-) girilmiş hatalı konut değerlerini 0'a eşitleme
df['residential_assets_value'] = df['residential_assets_value'].clip(lower=0)

asset_cols = ['residential_assets_value', 'commercial_assets_value', 'luxury_assets_value', 'bank_asset_value']
df['total_assets'] = df[asset_cols].sum(axis=1)
df['debt_to_income'] = df['loan_amount'] / df['income_annum']



df['Risk_Score'] = pd.qcut(df['cibil_score'], q=4, labels=[1, 2, 3, 4])
df['Wealth_Score'] = pd.qcut(df['total_assets'], q=4, labels=[1, 2, 3, 4])

def simple_crm_segment(row):
    r = int(row['Risk_Score'])
    w = int(row['Wealth_Score'])
    if r >= 3 and w >= 3:
        return '1_VIP_Musteri'
    elif r >= 3 and w < 3:
        return '2_Standart_Potansiyel'
    elif r < 3 and w >= 3:
        return '3_Teminat_Zengini_Riskli'
    else:
        return '4_Yuksek_Riskli'

df['CRM_Segment'] = df.apply(simple_crm_segment, axis=1)


urun_sozlugu = {
    '1_VIP_Musteri': 'Ozel Portfoy Yonetimi & Yatirim Fonu',
    '2_Standart_Potansiyel': 'Kredi Karti & Otomatik Odeme Talimati',
    '3_Teminat_Zengini_Riskli': 'Ipotek Teminatli Kredi (Limit Dusurerek Onay)',
    '4_Yuksek_Riskli': 'Blokeli Kredi Karti (Kredi Notu Yukseltme)'
}


df['Tavsiye_Edilen_Urun'] = df['CRM_Segment'].map(urun_sozlugu)


summary_table = df.groupby(['CRM_Segment', 'Tavsiye_Edilen_Urun']).agg(
    Musteri_Sayisi=('loan_id', 'count'),
    Ortalama_Gelir=('income_annum', 'mean'),
    Ortalama_Varlik=('total_assets', 'mean'),
    Ortalama_Kredi_Skoru=('cibil_score', 'mean'),
    Mevcut_Onay_Orani=('loan_status', lambda x: (x == 'Approved').mean() * 100)
).reset_index()


print("--- CRM SEGMENT ÖZET TABLOSU ---")
print(summary_table.to_string(index=False))


onayli_kredi_orani = (df[df['loan_status'] == 'Approved']['loan_amount'] / df['total_assets']).mean()

# Teminat zengini olup (3_Teminat_Zengini_Riskli) kredisi reddedilen müşterileri seçiyoruz
kurtarilacaklar = df[(df['CRM_Segment'] == '3_Teminat_Zengini_Riskli') & (df['loan_status'] == 'Rejected')].copy()

# Bu müşterilere, toplam varlıklarının güvenli oranını (onaylı oranının %80'i kadar güvenlik payı bırakarak) öneriyoruz
kurtarilacaklar['Onerilen_Revize_Limit'] = (kurtarilacaklar['total_assets'] * onayli_kredi_orani * 0.80).round(-5)

# --- SONUÇLARI EKRANA YAZDIRMA ---
print("\n--- KURTARILABİLİR MÜŞTERİLER İÇİN LİMİT TAVSİYESİ (İLK 5 KİŞİ) ---")
secilen_sutunlar = ['loan_id', 'income_annum', 'total_assets', 'cibil_score', 'loan_amount', 'Onerilen_Revize_Limit']
print(kurtarilacaklar[secilen_sutunlar].head().to_string(index=False))

# Genel toplam etki analizi
toplam_kurtarilan_musteri = len(kurtarilacaklar)
toplam_verilebilecek_kredi = kurtarilacaklar['Onerilen_Revize_Limit'].sum()
print(f"\n💡 Toplam Kurtarılabilir Müşteri Sayısı: {toplam_kurtarilan_musteri}")
print(f"💰 Bu müşterilere açılabilecek Toplam Güvenli Kredi Hacmi: {toplam_verilebilecek_kredi:,.0f} TL")

# Her segmentin müşteri payı (%)
pay = (df['CRM_Segment'].value_counts(normalize=True) * 100).round(1)

# Kurtarılabilir müşterilerden tahmini faiz geliri (varsayım: yıllık %12)
kurtarilacaklar['Geliri'] = kurtarilacaklar['Onerilen_Revize_Limit'] * 0.12
print(f"Tahmini yıllık geliri: {kurtarilacaklar['Geliri'].sum():,.0f}")

sira = ['1_VIP_Musteri', '2_Standart_Potansiyel', '3_Teminat_Zengini_Riskli', '4_Yuksek_Riskli']

# --- Grafik 0: CRM Segment Matrisi (ana görsel) ---
sayi = df['CRM_Segment'].value_counts()

fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)

kutular = [
    (0, 1, '#F9A825', f"Teminat Zengini\n{sayi['3_Teminat_Zengini_Riskli']} müşteri"),
    (1, 1, '#2E7D32', f"VIP\n{sayi['1_VIP_Musteri']} müşteri"),
    (0, 0, '#C62828', f"Yüksek Riskli\n{sayi['4_Yuksek_Riskli']} müşteri"),
    (1, 0, '#1976D2', f"Standart\n{sayi['2_Standart_Potansiyel']} müşteri"),
]
for x, y, renk, yazi in kutular:
    ax.add_patch(plt.Rectangle((x, y), 1, 1, color=renk, ec='white', lw=4))
    ax.text(x + 0.5, y + 0.5, yazi, ha='center', va='center', color='white', fontsize=14)

ax.set_xticks([0.5, 1.5])
ax.set_xticklabels(['Düşük Kredi Skoru', 'Yüksek Kredi Skoru'])
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(['Düşük Varlık', 'Yüksek Varlık'], rotation=90, va='center')
ax.tick_params(length=0)
ax.set_title('CRM Segment Matrisi')
plt.savefig('0_crm_matris.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Grafik 1: Korelasyon ısı haritası ---
sayisal = df.select_dtypes('number').drop(columns=['loan_id'], errors='ignore')

plt.figure(figsize=(10, 8))
sns.heatmap(sayisal.corr(), annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Değişkenler Arası Korelasyon')
plt.tight_layout()
plt.savefig('1_korelasyon.png', dpi=300)
plt.show()

# --- Grafik 2: Varlık histogramları ---
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
sns.histplot(data=df, x='residential_assets_value', hue='loan_status', element='step', ax=ax[0, 0])
sns.histplot(data=df, x='luxury_assets_value',      hue='loan_status', element='step', ax=ax[0, 1])
sns.histplot(data=df, x='commercial_assets_value',  hue='loan_status', element='step', ax=ax[1, 0])
sns.histplot(data=df, x='bank_asset_value',         hue='loan_status', element='step', ax=ax[1, 1])
ax[0, 0].set_title('Konut Varlığı')
ax[0, 1].set_title('Lüks Varlık')
ax[1, 0].set_title('Ticari Varlık')
ax[1, 1].set_title('Banka Varlığı')
plt.tight_layout()
plt.savefig('2_varlik_dagilimi.png', dpi=300)
plt.show()

# --- Grafik 3: Gelir - Kredi tutarı ---
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='income_annum', y='loan_amount', hue='loan_status')
plt.title('Yıllık Gelir ve Kredi Tutarı')
plt.xlabel('Yıllık Gelir')
plt.ylabel('Kredi Tutarı')
plt.savefig('3_gelir_kredi.png', dpi=300)
plt.show()

# --- Grafik 4: Segmentlere göre onay durumu ---
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x='CRM_Segment', hue='loan_status', order=sira)
plt.title('CRM Segmentlerine Göre Onay Durumu')
plt.xlabel('Segment')
plt.ylabel('Müşteri Sayısı')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('4_crm_segment.png', dpi=300)
plt.show()

# --- Grafik 5: Kredi skoru - Varlık (segmentlere göre renkli) ---
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='cibil_score', y='total_assets', hue='CRM_Segment', hue_order=sira)
plt.title('Kredi Skoru ve Toplam Varlık (CRM Segmentleri)')
plt.xlabel('Kredi Skoru')
plt.ylabel('Toplam Varlık')
plt.savefig('5_crm_scatter.png', dpi=300)
plt.show()

# --- Grafik 6: Kurtarılabilir müşteriler için önerilen limit dağılımı ---
plt.figure(figsize=(8, 5))
sns.histplot(kurtarilacaklar['Onerilen_Revize_Limit'], bins=20, color='#F9A825')
plt.title(f'Kurtarılabilir {len(kurtarilacaklar)} Müşteri: Önerilen Limit')
plt.xlabel('Önerilen Revize Limit')
plt.ylabel('Müşteri Sayısı')
plt.tight_layout()
plt.savefig('6_kurtarilabilir_limit.png', dpi=300)
plt.show()


