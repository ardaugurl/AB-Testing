import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#!pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.




#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç



#####################################################
# Proje Görevleri
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.




#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.

df_1 = pd.read_excel("/Users/ardaugurlu/Documents/miuul/measurement_problems/ABTesti/ab_testing.xlsx", "Control Group")
df_2 = pd.read_excel("/Users/ardaugurlu/Documents/miuul/measurement_problems/ABTesti/ab_testing.xlsx", "Test Group")


# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.
df_1.head()
df_1.describe().T
df_1.info()
df_1.shape
df_2.head()
df_2.describe().T

df_1["type_of_bidding"] = "maximum"
df_2["type_of_bidding"] = "average"
# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df = pd.concat([df_1, df_2])
df.reset_index()

#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.

#H0 : M1 == M2 (maximum bidding ve avarage bidding verileri arasında istatistiksel bir fark yoktur)
#H1 : M1 != M2 (.... vardır.)

#p value > 0.05 H0 reddedilemez.
# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz

df.groupby("type_of_bidding").agg({"Purchase" : "mean"})




#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

#NORMALLİK VARSAYIMI TESTİ
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1:..sağlanmamaktadır


test_stat, pvalue = shapiro(df.loc[df["type_of_bidding"] == "average", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

test_stat, pvalue = shapiro(df.loc[df["type_of_bidding"] == "maximum", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# her iki grup için de p value > 0.05 HO reddedilemez.

# Varyans homojenliği
# H0: Varyanslar Homojendir
# H1: Varyanslar Homojen Değildir



test_stat, pvalue = levene(df.loc[df["type_of_bidding"] == "average", "Purchase"].dropna(),
                           df.loc[df["type_of_bidding"] == "maximum", "Purchase"].dropna())

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

## P value > 0.05 H0 REDDEDİLEMEZ varyanslar homojendir.


# hem homojenlik testi hem de normallik testi sağlandığı için ttest kullanıcaz.

test_stat, pvalue = ttest_ind(df.loc[df["type_of_bidding"] == "average", "Purchase"],
                              df.loc[df["type_of_bidding"] == "maximum", "Purchase"],
                              equal_var=True) # 2 si de sağlandığı için True

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#P value > 0.05 H0 REDDEDİLEMEZ. Yani maximum bidding ve average bidding arasında istatiki bir fark yoktur.Ortalama farkı tamamen
#şans eseri oluşmuştur.