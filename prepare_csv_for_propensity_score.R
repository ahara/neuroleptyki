library(dplyr)

setwd('C:/Users/haras_000/Desktop/Neuroleptyki/Programy')

# Read data
neuroleptics <- read.csv('neuroleptyki_cleared.csv')
cardio <- read.csv('nasercowe_cleared.csv')

# Get rid of polish names
neuroleptics <- transmute(neuroleptics,
                          prescription_date = Data.realizacji.recepty,
                          id = Id.pacjenta,
                          sex = P.łeć...nazwa,
                          birth_year = Data.urodzenia..rok.,
                          death_year_month = Data.zgonu..rok.miesiąc.,
                          international_name = Nazwa.mi.dzynarodowa,
                          polish_name = Nazwa.leku,
                          dose = Dawka)
cardio <- transmute(cardio,
                    prescription_date = Data.realizacji.recepty,
                    id = Id.pacjenta,
                    sex = P.łeć...nazwa,
                    birth_year = Data.urodzenia..rok.,
                    death_year_month = Data.zgonu..rok.miesiąc.,
                    international_name = Nazwa.mi.dzynarodowa,
                    polish_name = Nazwa.leku,
                    dose = Dawka)

# Convert medicaments to generations
international_name <- as.character(neuroleptics$international_name)
international_name <- replace(international_name, international_name=='CHLORPROMAZINE', '1')
international_name <- replace(international_name, international_name=='CHLORPROTHIXENE', '1')
international_name <- replace(international_name, international_name=='CLOPENTHIXOL', '1')
international_name <- replace(international_name, international_name=='FLUPENTIXOL', '1')
international_name <- replace(international_name, international_name=='HALOPERIDOL', '1')
international_name <- replace(international_name, international_name=='LEVOMEPROMAZINE', '1')
international_name <- replace(international_name, international_name=='PERAZINE', '1')
international_name <- replace(international_name, international_name=='PERPHENAZINE', '1')
international_name <- replace(international_name, international_name=='PROCHLORPERAZINE', '1')
international_name <- replace(international_name, international_name=='PROMAZINE', '1')
international_name <- replace(international_name, international_name=='SULPIRIDE', '1')
international_name <- replace(international_name, international_name=='ZUCLOPENTHIXOL', '1')

international_name <- replace(international_name, international_name=='SERTINDOLE', 'Inne')
international_name <- replace(international_name, international_name=='TIAPRIDE', 'Inne')
neuroleptics$international_name <- international_name

# Summarise data about patients from neurolepics set
neuroleptics$sex <- as.character(neuroleptics$sex)
neuroleptics$death_year_month <- as.character(neuroleptics$death_year_month)
neuroleptics$prescription_date <- as.character(neuroleptics$prescription_date)
neuroleptics <- neuroleptics %>%
                group_by(id) %>%
                summarise(Zmarl = first(death_year_month) != '',
                          Plec = first(sex),
                          Data_urodzenia = first(birth_year),
                          Data_konca = if(Zmarl) first(death_year_month) else '2012-12',
                          Wiek = as.numeric(substr(min(prescription_date), 1, 4)) - first(birth_year),
                          Amisulpride_first  = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'AMISULPRIDE')),
                          Amisulpride_last   = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'AMISULPRIDE')),
                          Aripiprazole_first = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'ARIPIPRAZOLE')),
                          Aripiprazole_last  = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'ARIPIPRAZOLE')),
                          Clozapine_first    = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'CLOZAPINE')),
                          Clozapine_last     = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'CLOZAPINE')),
                          Risperidone_first  = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'RISPERIDONE')),
                          Risperidone_last   = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'RISPERIDONE')),
                          Olanzapine_first   = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'OLANZAPINE')),
                          Olanzapine_last    = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'OLANZAPINE')),
                          Quetiapine_first   = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'QUETIAPINE')),
                          Quetiapine_last    = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'QUETIAPINE')),
                          Ziprasidone_first  = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'ZIPRASIDONE')),
                          Ziprasidone_last   = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'ZIPRASIDONE')),
                          Inne_gen_2_first   = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Inne')),
                          Inne_gen_2_last    = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Inne')),
                          Gen_1_first        = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == '1')),
                          Gen_1_last         = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == '1')))

# Convert cardio medicaments to groups
international_name <- as.character(cardio$international_name)
international_name <- replace(international_name, international_name=='AMIODARONE', 'Nasercowe')
international_name <- replace(international_name, international_name=='DIGOXIN', 'Nasercowe')
international_name <- replace(international_name, international_name=='DRONEDARONE', 'Nasercowe')
international_name <- replace(international_name, international_name=='IVABRADINE', 'Nasercowe')
international_name <- replace(international_name, international_name=='ISOSORBIDE DINITRATE', 'Nasercowe')
international_name <- replace(international_name, international_name=='ISOSORBIDE MONONITRATE', 'Nasercowe')
international_name <- replace(international_name, international_name=='METILDIGOXIN', 'Nasercowe')
international_name <- replace(international_name, international_name=='MILRINONE', 'Nasercowe')
international_name <- replace(international_name, international_name=='MOLSIDOMINE', 'Nasercowe')
international_name <- replace(international_name, international_name=='PENTAERITHRITYL TETRANITRATE', 'Nasercowe')
international_name <- replace(international_name, international_name=='PROPAFENONE', 'Nasercowe')

international_name <- replace(international_name, international_name=='CHLORTALIDONE', 'Diuretyk')
international_name <- replace(international_name, international_name=='FUROSEMIDE', 'Diuretyk')
international_name <- replace(international_name, international_name=='HYDROCHLOROTHIAZIDE', 'Diuretyk')
international_name <- replace(international_name, international_name=='INDAPAMIDE', 'Diuretyk')
international_name <- replace(international_name, international_name=='CLOPAMIDE', 'Diuretyk')
international_name <- replace(international_name, international_name=='SPIRONOLACTONE', 'Diuretyk')
international_name <- replace(international_name, international_name=='TORASEMIDE', 'Diuretyk')

international_name <- replace(international_name, international_name=='ACEBUTOLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='ATENOLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='BETAXOLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='BISOPROLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='CELIPROLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='ESMOLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='CARVEDILOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='METOPROLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='NEBIVOLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='PINDOLOL', 'Beta-adrenolityk')
international_name <- replace(international_name, international_name=='SOTALOL', 'Beta-adrenolityk')

international_name <- replace(international_name, international_name=='AMLODIPINE', 'Antagonista wapnia')
international_name <- replace(international_name, international_name=='DILTIAZEM', 'Antagonista wapnia')
international_name <- replace(international_name, international_name=='FELODIPINE', 'Antagonista wapnia')
international_name <- replace(international_name, international_name=='LACIDIPINE', 'Antagonista wapnia')
international_name <- replace(international_name, international_name=='NIMODIPINE', 'Antagonista wapnia')
international_name <- replace(international_name, international_name=='NITRENDIPINE', 'Antagonista wapnia')
international_name <- replace(international_name, international_name=='VERAPAMIL', 'Antagonista wapnia')

international_name <- replace(international_name, international_name=='BENAZEPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='QUINAPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='CILAZAPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='ENALAPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='EPROSARTAN', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='IMIDAPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='IRBESARTAN', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='CANDESARTAN', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='CAPTOPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='LISINOPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='LOSARTAN', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='PERINDOPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='RAMIPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='TELMISARTAN', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='TRANDOLAPRIL', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='VALSARTAN', 'Renina-angiotensyna')
international_name <- replace(international_name, international_name=='ZOFENOPRIL', 'Renina-angiotensyna')

international_name <- replace(international_name, international_name=='ATORVASTATIN', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='CIPROFIBRATE', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='EZETIMIBE', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='FENOFIBRATE', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='FLUVASTATIN', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='COLESEVELAM', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='LOVASTATIN', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='PRAVASTATIN', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='ROSUVASTATIN', 'Lipidy w surowicy')
international_name <- replace(international_name, international_name=='SIMVASTATIN', 'Lipidy w surowicy')

international_name <- replace(international_name, international_name=='INSULIN', 'Insulina')
international_name <- replace(international_name, international_name=='INSULIN ASPART', 'Insulina')
international_name <- replace(international_name, international_name=='INSULIN DETEMIR', 'Insulina')
international_name <- replace(international_name, international_name=='INSULIN GLARGINE', 'Insulina')
international_name <- replace(international_name, international_name=='INSULIN GLULISINE', 'Insulina')
international_name <- replace(international_name, international_name=='INSULIN LISPRO', 'Insulina')

international_name <- replace(international_name, international_name=='METFORMIN', 'Leki hipoglikemizujace')
international_name <- replace(international_name, international_name=='GLICLAZIDE', 'Leki hipoglikemizujace')
international_name <- replace(international_name, international_name=='GLIQUIDONE', 'Leki hipoglikemizujace')
international_name <- replace(international_name, international_name=='GLIMEPIRIDE', 'Leki hipoglikemizujace')
international_name <- replace(international_name, international_name=='GLIPIZIDE', 'Leki hipoglikemizujace')
international_name <- replace(international_name, international_name=='PIOGLITAZONE', 'Leki hipoglikemizujace')
international_name <- replace(international_name, international_name=='ACARBOSE', 'Leki hipoglikemizujace')
cardio$international_name <- international_name

# Summarise data about medicaments from cardio set
cardio$prescription_date <- as.character(cardio$prescription_date)
cardio <- cardio %>%
          group_by(id) %>%
          summarise(Nasercowe_First         = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Nasercowe')),
                    Nasercowe_Last          = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Nasercowe')),
                    Diuretyk_First          = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Diuretyk')),
                    Diuretyk_Last           = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Diuretyk')),
                    Beta_adrenolityk_First  = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Beta-adrenolityk')),
                    Beta_adrenolityk_Last   = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Beta-adrenolityk')),
                    Antagonista_First       = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Antagonista wapnia')),
                    Antagonista_Last        = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Antagonista wapnia')),
                    Renina_First            = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Renina-angiotensyna')),
                    Renina_Last             = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Renina-angiotensyna')),
                    Lipidy_First            = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Lipidy w surowicy')),
                    Lipidy_Last             = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Lipidy w surowicy')),
                    Insulina_First          = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Insulina')),
                    Insulina_Last           = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Insulina')),
                    Hipoglikemizujace_First = min(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Leki hipoglikemizujace')),
                    Hipoglikemizujace_Last  = max(subset(prescription_date, prescription_date < '2012-07-01' & international_name == 'Leki hipoglikemizujace')))

# Join neuroleptics and cardio
neuroleptics_and_cardio <- left_join(neuroleptics, cardio)

# Transmute data to final form
neuroleptics_generation_2 <- c('Amisulpride',
                               'Aripiprazole',
                               'Clozapine',
                               'Risperidone',
                               'Olanzapine',
                               'Quetiapine',
                               'Ziprasidone',
                               'Inne_gen_2')
final <- neuroleptics_and_cardio
for (drug in neuroleptics_generation_2) {
  drug_first <- final[[paste(drug, '_first', sep='')]]
  final[[drug]] <- !is.na(drug_first)
  final[[paste(drug, '_gen_1', sep='')]]             <- !is.na(final$Gen_1_first)             & (final[[drug]] == FALSE | final$Gen_1_first < drug_first)
  final[[paste(drug, '_Nasercowe', sep='')]]         <- !is.na(final$Nasercowe_First)         & (final[[drug]] == FALSE | final$Nasercowe_First < drug_first)
  final[[paste(drug, '_Diuretyk', sep='')]]          <- !is.na(final$Diuretyk_First)          & (final[[drug]] == FALSE | final$Diuretyk_First < drug_first)
  final[[paste(drug, '_Beta_adrenolityk', sep='')]]  <- !is.na(final$Beta_adrenolityk_First)  & (final[[drug]] == FALSE | final$Beta_adrenolityk_First < drug_first)
  final[[paste(drug, '_Antagonista', sep='')]]       <- !is.na(final$Antagonista_First)       & (final[[drug]] == FALSE | final$Antagonista_First < drug_first)
  final[[paste(drug, '_Renina', sep='')]]            <- !is.na(final$Renina_First)            & (final[[drug]] == FALSE | final$Renina_First < drug_first)
  final[[paste(drug, '_Lipidy', sep='')]]            <- !is.na(final$Lipidy_First)            & (final[[drug]] == FALSE | final$Lipidy_First < drug_first)
  final[[paste(drug, '_Insulina', sep='')]]          <- !is.na(final$Insulina_First)          & (final[[drug]] == FALSE | final$Insulina_First < drug_first)
  final[[paste(drug, '_Hipoglikemizujace', sep='')]] <- !is.na(final$Hipoglikemizujace_First) & (final[[drug]] == FALSE | final$Hipoglikemizujace_First < drug_first)
}

# Write results to CSV file
write.csv(final, 'neuroleptyki_propensity_score.csv', row.names = FALSE, na='')
