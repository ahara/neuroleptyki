library(dplyr)

setwd('C:/Users/haras_000/Desktop/Neuroleptyki/Programy')

# Read data
df_2008_2010 <- read.csv('../Dane/neuroleptyki_2008-2010.csv', sep=';')
df_2011_2012 <- read.csv('../Dane/neuroleptyki_2011-2012.csv', sep=';')

# Concatenate data
df_2008_2012 <- rbind(df_2008_2010, df_2011_2012)

# Remove unnecessary variables - free memory
df_2008_2010 <- NULL
df_2011_2012 <- NULL

# Fix coding issue with polish characters
df_2008_2012$P.³eæ...nazwa <- replace(as.character(df_2008_2012$P.³eæ...nazwa),
                                      df_2008_2012$P.³eæ...nazwa=='m©¾czyzna',
                                      'mezczyzna')

# Data cleaning
buyers_age <- as.integer(format(as.POSIXct(df_2008_2012$Data.realizacji.recepty), format='%Y')) - as.integer(as.character(df_2008_2012$Data.urodzenia..rok.))
df_right_age <- subset(df_2008_2012, buyers_age >= 3)
buyers_death <- as.character(df_right_age$Data.zgonu..rok.miesi¹c.)
buyers_death <- replace(buyers_death, buyers_death=='', '2014-10')
df_right_age <- subset(df_right_age, as.character(df_right_age$Data.realizacji.recepty) < paste(buyers_death, '32', sep='-'))

# Unified units in Dose/Dawka field
unified_dose <- as.character(df_right_age$Dawka)
unified_dose <- replace(unified_dose, unified_dose=='400 mg', '0.4')
unified_dose <- replace(unified_dose, unified_dose=='4%', '0.04')
unified_dose <- replace(unified_dose, unified_dose=='0,5 MG', '0.0005')
unified_dose <- replace(unified_dose, unified_dose=='0,405 G', '0.405')
unified_dose <- replace(unified_dose, unified_dose=='0,4 G', '0.4')
unified_dose <- replace(unified_dose, unified_dose=='0,3 G', '0.3')
unified_dose <- replace(unified_dose, unified_dose=='0,25 G', '0.25')
unified_dose <- replace(unified_dose, unified_dose=='0,21 G', '0.21')
unified_dose <- replace(unified_dose, unified_dose=='0,2%', '0.002')
unified_dose <- replace(unified_dose, unified_dose=='0,2 G/1 ML', '0.2')
unified_dose <- replace(unified_dose, unified_dose=='0,2 G', '0.2')
unified_dose <- replace(unified_dose, unified_dose=='0,15 G', '0.15')
unified_dose <- replace(unified_dose, unified_dose=='0,2 G', '0.2')
unified_dose <- replace(unified_dose, unified_dose=='0,1 G/5 ML', '0.1')
unified_dose <- replace(unified_dose, unified_dose=='0,15 G', '0.15')
unified_dose <- replace(unified_dose, unified_dose=='0,1 G/2 ML', '0.1')
unified_dose <- replace(unified_dose, unified_dose=='0,1 G/1 ML', '0.1')
unified_dose <- replace(unified_dose, unified_dose=='0,1 G', '0.1')
unified_dose <- replace(unified_dose, unified_dose=='0,08 G', '0.08')
unified_dose <- replace(unified_dose, unified_dose=='0,06 G', '0.06')
unified_dose <- replace(unified_dose, unified_dose=='0,05 G/1 ML', '0.05')
unified_dose <- replace(unified_dose, unified_dose=='0,05 G', '0.05')
unified_dose <- replace(unified_dose, unified_dose=='0,04 G/2 ML', '0.04')
unified_dose <- replace(unified_dose, unified_dose=='0,04 G', '0.04')
unified_dose <- replace(unified_dose, unified_dose=='0,0375 G', '0.0375')
unified_dose <- replace(unified_dose, unified_dose=='0,025 G/5 ML', '0.025')
unified_dose <- replace(unified_dose, unified_dose=='0,025 G/1 ML', '0.025')
unified_dose <- replace(unified_dose, unified_dose=='0,025 G', '0.025')
unified_dose <- replace(unified_dose, unified_dose=='0,02 G', '0.02')
unified_dose <- replace(unified_dose, unified_dose=='0,02 G/1 ML', '0.02')
unified_dose <- replace(unified_dose, unified_dose=='0,016 G', '0.016')
unified_dose <- replace(unified_dose, unified_dose=='0,015 G', '0.015')
unified_dose <- replace(unified_dose, unified_dose=='0,012 G', '0.012')
unified_dose <- replace(unified_dose, unified_dose=='0,01 G', '0.01')
unified_dose <- replace(unified_dose, unified_dose=='0,008 G', '0.008')
unified_dose <- replace(unified_dose, unified_dose=='0,0075 G', '0.0075')
unified_dose <- replace(unified_dose, unified_dose=='0,005 G/1 ML', '0.005')
unified_dose <- replace(unified_dose, unified_dose=='0,005 G', '0.005')
unified_dose <- replace(unified_dose, unified_dose=='0,004 G', '0.004')
unified_dose <- replace(unified_dose, unified_dose=='0,003 G', '0.003')
unified_dose <- replace(unified_dose, unified_dose=='0,002 G', '0.002')
unified_dose <- replace(unified_dose, unified_dose=='0,001 G/1 ML', '0.001')
unified_dose <- replace(unified_dose, unified_dose=='0,001 G', '0.001')

df_right_age$Dawka <- unified_dose

# Write results to CSV file
write.csv(df_right_age, 'neuroleptyki_cleared.csv', row.names=FALSE, na='')
