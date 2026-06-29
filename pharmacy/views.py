import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from groq import Groq
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Medicament, Vente, Etablissement, PharmaciePartenaire

# Initialisation optionnelle de Groq (S'appuie sur votre variable d'environnement existante)
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception:
    groq_client = None


@login_required
def inventaire(request):
    """Affiche la liste des médicaments uniquement aux utilisateurs connectés"""
    tous_les_medicaments = Medicament.objects.all()
    return render(request, 'pharmacy/inventaire.html', {
        'medicaments': tous_les_medicaments
    })


@login_required
def passer_vente_gros(request):
    """Gère la facturation et le déstockage massif par cartons de gros avec déduction ANTI-FRAUDE"""
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)
    etablissements = Etablissement.objects.all()

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_cartons = int(request.POST.get("quantite_cartons", 0))
        etablissement_id = request.POST.get("etablissement")

        medicament = get_object_or_404(Medicament, id=medicament_id)
        unites_demandees = quantite_cartons * medicament.unites_par_carton

        # 1. Vérification stricte et inviolable du stock disponible
        if medicament.quantite_stock < unites_demandees:
            messages.error(
                request,
                f"Opération refusée ! Stock insuffisant pour {medicament.nom}."
            )
            return redirect("passer_vente_gros")

        try:
            # SÉCURITÉ RENFORCÉE : Soustraction immédiate et définitive du stock central
            medicament.quantite_stock -= unites_demandees
            medicament.save()

            # 2. Enregistrement comptable de la transaction de gros
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='GROS',
                quantite_vendue=quantite_cartons,
            )

            # 3. Redirection directe vers la page de la facture exclusive
            return redirect("afficher_facture_gros", username=None, vente_id=vente.id)

        except Exception as e:
            messages.error(request, f"Erreur d'exécution du module : {str(e)}")
            return redirect("passer_vente_gros")

    return render(request, "pharmacy/vente_gros.html", {
        "medicaments": medicaments,
        "etablissements": etablissements
    })


@login_required
def afficher_facture_gros(request, username=None, vente_id=None):
    """Affiche le reçu officiel d'une vente de gros pour impression sans erreur de type"""
    target_id = vente_id if vente_id else username
    vente = get_object_or_404(Vente, id=target_id)

    # 1. Calcul du prix total (génère un type Decimal via les champs du modèle)
    prix_total_cartons = vente.quantite_vendue * (vente.medicament.prix_unitaire * vente.medicament.unites_par_carton)

    # 2. Sécurisation mathématique : Conversion du taux float en Decimal
    redevance = prix_total_cartons * Decimal('0.05')

    # 3. Addition des deux montants de même type (Decimal)
    montant_total_sih = prix_total_cartons + redevance

    return render(request, "pharmacy/facture_gros.html", {
        "vente": vente,
        "prix_total_cartons": prix_total_cartons,
        "redevance": redevance,
        "montant_total_sih": montant_total_sih
    })


@login_required
def passer_vente_detail(request):
    """Gère la distribution au détail (à l'unité) pour les patients de l'hôpital"""
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_unites = int(request.POST.get("quantite_unites", 0))

        medicament = get_object_or_404(Medicament, id=medicament_id)

        # 1. Vérification stricte du stock disponible à l'unité
        if medicament.quantite_stock < quantite_unites:
            messages.error(
                request,
                f"Alerte Stock ! Il ne reste que {medicament.quantite_stock} unités de {medicament.nom}."
            )
            return redirect("passer_vente_detail")

        try:
            # 2. Déduction unique et sécurisée du stock avant enregistrement
            medicament.quantite_stock -= quantite_unites
            medicament.save()

            # 3. Enregistrement de la vente de type 'DETAIL'
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='DETAIL',
                quantite_vendue=quantite_unites,
            )           
            # 4. Redirection forcée immédiate pour vider le formulaire
            return redirect("afficher_facture_detail", vente_id=vente.id)

        except Exception as e:
            messages.error(request, f"Erreur système : {str(e)}")
            return redirect("passer_vente_detail")

    return render(request, "pharmacy/vente_detail.html", {
        "medicaments": medicaments
    })


@login_required
def afficher_facture_detail(request, vente_id):
    """Génère le reçu au détail pour le dossier du patient"""
    vente = get_object_or_404(Vente, id=vente_id)

    # Calcul au détail : Unités vendues x Prix unitaire de base
    montant_total_unitaire = vente.quantite_vendue * vente.medicament.prix_unitaire

    return render(request, "pharmacy/facture_detail.html", {
        "vente": vente,
        "montant_total_unitaire": montant_total_unitaire
    })


@login_required
def passer_transfert(request):
    """Transfère des cartons de médicaments vers un autre établissement sanitaire"""
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)
    etablissements = Etablissement.objects.all()

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_cartons = int(request.POST.get("quantite_cartons", 0))
        etablissement_id = request.POST.get("etablissement")

        medicament = get_object_or_404(Medicament, id=medicament_id)
        etablissement = get_object_or_404(Etablissement, id=etablissement_id)

        unites_demandees = quantite_cartons * medicament.unites_par_carton

        # Validation stricte de la capacité logistique
        if medicament.quantite_stock < unites_demandees:
            messages.error(
                request,
                f"Transfert avorté ! Stock insuffisant pour expédier {quantite_cartons} cartons."
            )
            return redirect("passer_transfert")

        try:
            # Soustraction unique du stock central
            medicament.quantite_stock -= unites_demandees
            medicament.save()

            # Enregistrement du mouvement logistique
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='GROS',
                quantite_vendue=quantite_cartons,
            )

            # Redirection vers la génération du Bon de Transport Officiel
            return redirect("afficher_bon_transfert", vente_id=vente.id, etab_id=etablissement.id)

        except Exception as e:
            messages.error(request, f"Échec de l'ordre de transfert : {str(e)}")
            return redirect("passer_transfert")

    return render(request, "pharmacy/transfert.html", {
        "medicaments": medicaments,
        "etablissements": etablissements
    })


@login_required
def afficher_bon_transfert(request, vente_id, etab_id):                           
    """Génère le Bon de Convoi officiel pour le transport routier"""
    vente = get_object_or_404(Vente, id=vente_id)
    etablissement = get_object_or_404(Etablissement, id=etab_id)

    volume_total = vente.quantite_vendue * vente.medicament.unites_par_carton

    return render(request, "pharmacy/bon_transfert.html", {
        "vente": vente,
        "etablissement": etablissement,
        "volume_total": volume_total
    })


@login_required
def rapport_flux(request):
    """Affiche le journal historique de toutes les transactions de stock"""
    mouvements = Vente.objects.all().order_by('-date_vente')
    return render(request, "pharmacy/rapport_flux.html", {
        "mouvements": mouvements
    })


@login_required
def hologramme_ia_view(request):
    """Affiche l'interface de l'Hologramme et gère l'interaction par Chat Textuel Groq"""                     
    reponse_texte = None

    if request.method == "POST":
        message_patient = request.POST.get("message", "").strip()
        zone_patient = request.POST.get("zone", "Gombe").strip()

        if message_patient and groq_client:
            try:
                # MODÈLE CORRIGÉ ET VALIDE SUR GROQ CLOUD
                completion = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Tu es Vonda, l'intelligence artificielle conversationnelle du conglomérat SIH. "
                                "Réponds de manière rassurante et brève. Si le patient formule une recherche de médicament, "
                                "ajoute impérativement cette balise exacte à la toute fin de ton message : [RECHERCHE: nom_du_medicament]"
                            )
                        },
                        {"role": "user", "content": message_patient}
                    ],
                    temperature=0.4,
                )                                       
                brut_reponse = completion.choices[0].message.content

                # 2. Traitement et extraction automatique du radar d'alertes
                if "[RECHERCHE:" in brut_reponse:
                    partie_medicament = brut_reponse.split("[RECHERCHE:")[1].split("]")[0].strip()
                    reponse_texte = brut_reponse.split("[RECHERCHE:")[0].strip()

                    # 3. Recherche des pharmacies affiliées dans la zone
                    pharmacies_affiliees = PharmaciePartenaire.objects.filter(
                        zone_ville__icontains=zone_patient,
                        est_affiliee=True
                    )

                    # 4. Expédition automatique des notifications WhatsApp par Twilio
                    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")

                    if twilio_sid and twilio_token and pharmacies_affiliees.exists():
                        client_twilio = Client(twilio_sid, twilio_token)
                        twilio_number = "whatsapp:+14155238886"

                        for pharmacie in pharmacies_affiliees:
                            if "angola" in pharmacie.pays.lower():
                                texte_whatsapp = (
                                    f"🚨 *VONDA RADAR ALERTA* 🚨\n\n"
                                    f"Olá Gerência da {pharmacie.nom},\n"
                                    f"Um paciente na sua zona ({zone_patient}) está à procura de: *{partie_medicament}*\n"
                                    f"Sincronize o seu stock para garantir esta venda!"
                                )
                            else:
                                texte_whatsapp = (
                                    f"🚨 *VONDA RADAR ALERTE* 🚨\n\n"
                                    f"Direction {pharmacie.nom},\n"
                                    f"Un patient recherche actuellement ce produit dans votre zone ({zone_patient}) : *{partie_medicament}*\n"
                                    f"Veuillez vérifier vos stocks sur votre interface !"
                                )

                            client_twilio.messages.create(
                                body=texte_whatsapp,
                                from_=twilio_number,
                                to=f"whatsapp:+{pharmacie.telephone_whatsapp}"
                            )
                else:
                    reponse_texte = brut_reponse

            except Exception as e:
                reponse_texte = f"Système momentanément surchargé. (Erreur: {str(e)})"

    return render(request, 'pharmacy/hologramme_ia.html', {
        'reponse_texte': reponse_texte
    })


@csrf_exempt
def twilio_webhook(request):
    """
    📡 ROUTE ESSENTIELLE : Webhook Twilio pour recevoir et répondre en direct sur WhatsApp.
    Reçoit la phrase du patient, l'analyse via Groq et déclenche le réseau d'alertes.
    """
    response = MessagingResponse()
    
    if request.method == "POST":
        message_patient = request.POST.get("Body", "").strip()
        zone_patient = "Gombe" 
        
        if message_patient and groq_client:
            try:
                # MODÈLE CORRIGÉ ET VALIDE SUR GROQ CLOUD
                completion = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Tu es Vonda, l'intelligence artificielle du conglomérat SIH. "
                                "Réponds de façon concise, professionnelle et chaleureuse. "
                                "RÈGLE ABSOLUE ET CRITIQUE : Tu dois répondre EXCLUSIVEMENT et ENTIÈREMENT dans la langue utilisée par l'utilisateur. "
                                "Si l'utilisateur écrit en Swahili, réponds à 100% en Swahili. Si c'est en Anglais, réponds en Anglais. Si c'est en Portugais, réponds en Portugais. "
                                "Ne traduis JAMAIS ta réponse en français si l'utilisateur t'interpelle dans une autre langue. "
                                "Si l'utilisateur recherche un médicament, ajoute obligatoirement ceci à la toute fin : [RECHERCHE: nom_du_produit]"
                            )
                        },
                        {"role": "user", "content": message_patient}
                    ],
                    temperature=0.4,
                )
                brut_reponse = completion.choices[0].message.content

                if "[RECHERCHE:" in brut_reponse:
                    partie_medicament = brut_reponse.split("[RECHERCHE:")[1].split("]")[0].strip()
                    texte_a_renvoyer = brut_reponse.split("[RECHERCHE:")[0].strip()

                    pharmacies_affiliees = PharmaciePartenaire.objects.filter(
                        zone_ville__icontains=zone_patient,
                        est_affiliee=True
                    )
                    
                    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")

                    if twilio_sid and twilio_token and pharmacies_affiliees.exists():
                        client_twilio = Client(twilio_sid, twilio_token)
                        twilio_number = "whatsapp:+14155238886"

                        for pharmacie in pharmacies_affiliees:
                            if "angola" in pharmacie.pays.lower():
                                texte_whatsapp = (
                                    f"🚨 *VONDA RADAR ALERTA* 🚨\n\n"
                                    f"Olá Gerência da {pharmacie.nom},\n"
                                    f"Um paciente na sua zona está à procura de: *{partie_medicament}*\n"
                                )
                            else:
                                texte_whatsapp = (
                                    f"🚨 *VONDA RADAR ALERTE* 🚨\n\n"
                                    f"Direction {pharmacie.nom},\n"
                                    f"Un patient recherche ce produit dans votre zone ({zone_patient}) : *{partie_medicament}*\n"
                                )
                            
                            client_twilio.messages.create(
                                body=texte_whatsapp,
                                from_=twilio_number,
                                to=f"whatsapp:+{pharmacie.telephone_whatsapp}"
                            )
                    
                    response.message(texte_a_renvoyer)
                else:
                    response.message(brut_reponse)

            except Exception as e:
                print("❌ ERREUR GROQ WEBHOOK :", str(e))
                response.message("Vonda SIH : Une erreur est survenue lors de l'analyse.")
        else:
            response.message("Vonda SIH : Connexion IA indisponible.")
            
    return HttpResponse(str(response), content_type='application/xml')


@login_required
def API_recherche_radar_ia(request):
    """
    Moteur de recherche topographique et prédictif pour l'Hologramme IA.
    Scanne les stocks réels, les arrivages (lots) et l'historique transfrontalier.
    """
    terme_recherche = request.GET.get('medicament', '').strip()

    if not terme_recherche:
        return JsonResponse({"statut": "vide", "message": "Aucun produit spécifié."})

    stocks_trouves = Medicament.objects.filter(
        Q(nom__icontains=terme_recherche) | Q(numero_lot_import__icontains=terme_recherche)
    ).select_related('etablissement')

    resultats_officines = []
    arrivages_futurs = []

    for med in stocks_trouves:
        cartons = 0
        if med.unites_par_carton and med.unites_par_carton > 0:
            cartons = med.quantite_stock // med.unites_par_carton          
        if med.quantite_stock > 0:
            resultats_officines.append({
                "pharmacie": med.etablissement.nom,
                "adresse": med.etablissement.adresse,
                "pays": med.pays_origine,
                "stock_unites": med.quantite_stock,
                "stock_cartons": cartons,
                "prix": float(med.prix_unitaire),
                "statut": "DISPONIBLE IMMÉDIATEMENT"
            })
        else:
            if med.numero_lot_import or med.cout_fret_douane > 0:
                arrivages_futurs.append({
                    "depot_destination": med.etablissement.nom,
                    "numero_lot": med.numero_lot_import,
                    "provenance": med.pays_origine,
                    "fret_douane_applique": float(med.cout_fret_douane),
                    "statut": "EN COURS D'ARRIVAGE / TRANSIT DOUANIER"
                })

    return JsonResponse({
        "statut": "succes",
        "produit_recherche": terme_recherche,
        "disponibilites_immédiates": resultats_officines,
        "radar_arrivages_previsionnels": arrivages_futurs,
        "total_sites_allies": len(resultats_officines) + len(arrivages_futurs)
    })
