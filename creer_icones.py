from PIL import Image, ImageDraw
import os

def generer_logo_lisible():
    dossier = 'static/images'
    if not os.path.exists(dossier): os.makedirs(dossier)
    
    # Créer un cercle bleu pro
    taille = 512
    img = Image.new('RGBA', (taille, taille), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 502, 502], fill=(44, 62, 80))
    
    # Dessiner un grand "V" blanc (plus lisible que du petit texte)
    points = [(150, 150), (256, 400), (362, 150)]
    draw.line(points, fill="white", width=40)

    img.save('logo_brut.png')
    for t in [192, 512]:
        img.resize((t, t), Image.Resampling.LANCZOS).save(f"{dossier}/icon-{t}x{t}.png")
    print("✅ Logo simplifié et icônes générées !")

if __name__ == "__main__":
    generer_logo_lisible()
