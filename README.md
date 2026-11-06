# credit-risk-crm-segmentation
Kredi Tahsisinde Varlık Tabanlı Müşteri Kurtarma &amp; CRM Segmentasyonu
# 🏦 Kredi Tahsisinde Varlık Tabanlı Müşteri Kurtarma & Analitik CRM Segmentasyonu

Bu proje, geleneksel kredi tahsis motorlarının skor bazlı kural kısıtları nedeniyle doğrudan elediği teminat gücü yüksek müşterileri tespit etmek ve **güvenlik marjlı dinamik limit revizyonu** ile portföye kazandırmak amacıyla geliştirilmiştir.

---

## 📌 Proje Özeti
* **Veri Seti:** 4.269 bireysel kredi başvurusu (Kaggle Loan Approval Dataset)
* **Temel Metodoloji:** Kredi Bürosu Skoru (CIBIL) ve Toplam Varlık Büyüklüğü eksenlerinde $2 \times 2$ çeyreklik (quartile) matris segmentasyonu
* **Temel Tespit:** 1.091 kişilik "Teminat Zengini Riskli" grubun %75,5'i (824 müşteri) yalnızca skoru nedeniyle veto edilmiş durumdadır.
* **Çözüm:** Sağlıklı portföyün teminat karşılama rasyosu üzerinden %20 iskonto (haircut) ile dinamik limit tahsisi.

---

## 📊 CRM Segmentasyon Matrisi
Müşteriler risk ve bilanço güçlerine göre 4 ana profile ayrılmıştır:

![CRM Matrisi]<img width="1744" height="1796" alt="0_crm_matris" src="https://github.com/user-attachments/assets/208063b5-7461-483a-98ae-0fa62062fc9b" />


1. **1_VIP_Musteri:** Yüksek skor, yüksek varlık (Özel portföy & fon ürünleri)
2. **2_Standart_Potansiyel:** Yüksek skor, düşük/orta varlık (Maaş müşterisi / tüketici kredisi)
3. **3_Teminat_Zengini_Riskli:** Düşük skor, yüksek varlık (**İpotek teminatlı kurtarma odağı**)
4. **4_Yuksek_Riskli:** Düşük skor, düşük varlık (Blokeli/teminatlı mikro kartlar)

---

## ⚙️ Dinamik Limit Kurtarma Modeli

Kural motoru tarafından reddedilen 824 teminat zengini müşteri için uygulanan revize limit fonksiyonu:

$$\text{Önerilen Limit} = \text{Toplam Varlık} \times \left(\frac{\text{Onaylı Kredi Tutarı}}{\text{Toplam Varlık}}\right)_{\text{ortalama}} \times 0.80$$

### Çıktılar:
* **Kurtarılan Müşteri Sayısı:** 824
* **Ortalama Kurtarılan Limit Dağılımı:**

![Kurtarılan Limit Dağılımı](figures/6_kurtarilabilir_limit.png)

---

## 🚀 Kurulum ve Çalıştırma

```bash
git clone [https://github.com/Yakuza61-fintech/credit-risk-crm-segmentation](https://github.com/Yakuza61-fintech/credit-risk-crm-segmentation)
cd credit-risk-crm-segmentation
pip install -r requirements.txt
python src/analysis.py
