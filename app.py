import io
import logging
import os
from flask import Flask, render_template, render_template_string, request, flash, redirect, url_for
from flask_mail import Mail, Message
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super-secret-key-for-flashing')

# --- EMAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'mathayoisaya40@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'spwktancwnodstsi')
app.config['MAIL_DEFAULT_SENDER'] = ('Pardalis Safari Tour', app.config['MAIL_USERNAME'])

ADMIN_EMAIL = 'mathayoisaya40@gmail.com'

mail = Mail(app)

# Setup logging
logging.basicConfig(level=logging.INFO)


def generate_pdf(html_content):
    """Converts HTML content into an in-memory PDF file."""
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer if not pisa_status.err else None


# SHARED TEMPLATE FOR DYNAMIC NAVIGATION PAGES
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | Pardalis Safari Tours</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; }
body { background-color: #f7f5f0; color: #333; line-height: 1.5; font-size: 14px; }
header { background-color: #ffffff; padding: 15px 20px; text-align: center; border-bottom: 1px solid #e2e2e2; }
.header-container { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }
.logo-container img { max-height: 90px; width: auto; display: block; }
.slogan { margin-top: 8px; font-size: 0.95rem; font-weight: bold; color: #5c3a21; text-transform: uppercase; letter-spacing: 0.8px; }

nav { background-color: #4A1208; border-top: 1px solid #5c180b; border-bottom: 3px solid #2B0601; position: sticky; top: 0; z-index: 1000; }
.nav-container { max-width: 1200px; margin: 0 auto; }
.nav-menu { list-style: none; display: flex; justify-content: flex-start; align-items: center; flex-wrap: wrap; }
.nav-item > a { display: flex; align-items: center; gap: 5px; padding: 12px 16px; color: #ffffff; text-decoration: none; font-weight: bold; font-size: 0.85rem; text-transform: uppercase; transition: background-color 0.2s; }
.nav-item:hover > a { background-color: #2B0601; }

.page-wrapper { max-width: 1250px; margin: 20px auto; padding: 0 15px; }
.main-content { background: #ffffff; padding: 25px; border: 1px solid #e0d7c6; border-radius: 4px; }
.main-title { color: #4A1208; font-size: 1.75rem; text-transform: uppercase; margin-bottom: 10px; }
.subtitle { color: #8B4513; font-size: 1.05rem; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #d4a359; padding-bottom: 8px; }

.gallery-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
.gallery-card { background: #fcfbfa; border: 1px solid #e2dacd; border-top: 3px solid #4A1208; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s ease, box-shadow 0.2s ease; }
.gallery-card:hover { transform: translateY(-3px); box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.gallery-card a { text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }
.gallery-card img { width: 100%; height: 200px; object-fit: cover; }
.gallery-card-body { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
.gallery-card-body h3 { color: #4A1208; margin-bottom: 8px; font-size: 1.1rem; text-transform: uppercase; }
.gallery-card-body p { font-size: 0.85rem; color: #555; line-height: 1.5; }
.explore-btn { margin-top: 12px; color: #8B4513; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; }

footer { background-color: #2b180d; color: #d4a359; padding: 20px 15px; text-align: center; border-top: 3px solid #4A1208; margin-top: 30px; }
footer p { color: #e0d5c1; font-size: 0.8rem; }
</style>
</head>
<body>
<header>
    <div class="header-container">
        <div class="logo-container">
            <img src="{{ url_for('static', filename='logo.png') }}" alt="Pardalis Safari Tours Logo">
        </div>
        <div class="slogan">Great People for Memorable Safaris</div>
    </div>
</header>

<nav>
    <div class="nav-container">
        <ul class="nav-menu">
            <li class="nav-item"><a href="{{ url_for('home') }}">HOME</a></li>
            <li class="nav-item"><a href="{{ url_for('about') }}">ABOUT US</a></li>
            <li class="nav-item"><a href="{{ url_for('destinations') }}">DESTINATIONS</a></li>
            <li class="nav-item"><a href="{{ url_for('safaris') }}">SAFARIS</a></li>
            <li class="nav-item"><a href="{{ url_for('climbing_trekking') }}">CLIMBING & TREKKING</a></li>
            <li class="nav-item"><a href="{{ url_for('accommodation') }}">ACCOMMODATION</a></li>
        </ul>
    </div>
</nav>

<div class="page-wrapper">
    <main class="main-content">
        <h1 class="main-title">{{ heading }}</h1>
        <div class="subtitle">{{ subheading }}</div>
        <p>{{ description }}</p>

        <div class="gallery-grid">
            {% for item in items %}
            <div class="gallery-card">
                <a href="{{ item.link if item.link else '#' }}">
                    <img src="{{ item.image }}" alt="{{ item.title }}">
                    <div class="gallery-card-body">
                        <div>
                            <h3>{{ item.title }}</h3>
                            <p>{{ item.text }}</p>
                        </div>
                        {% if item.link %}
                        <div class="explore-btn">Explore Details &rarr;</div>
                        {% endif %}
                    </div>
                </a>
            </div>
            {% endfor %}
        </div>
    </main>
</div>

<footer>
    <p>&copy; 2026 Pardalis Safari Tours. All Rights Reserved. | Designed for Memorable Safaris</p>
</footer>
</body>
</html>
"""

# --- GENERAL ROUTES ---

@app.route('/')
def home():
    """Renders the main Leopard Tours style homepage."""
    return render_template('index.html')


@app.route('/book', endpoint='booking_page')
@app.route('/book_form', endpoint='booking_form')
def booking_page():
    """Renders the dedicated safari booking form page."""
    return render_template('book.html')


@app.route('/handle_booking', methods=['POST'])
def handle_booking():
    recipient_email = request.form.get('email')

    if not recipient_email:
        logging.error("No email address provided in the form submission.")
        flash("Email is required to complete your booking.", "danger")
        return redirect(url_for('booking_page'))

    booking_data = {
        'first_name': request.form.get('first_name', 'Valued'),
        'last_name': request.form.get('last_name', 'Guest'),
        'country': request.form.get('country', 'N/A'),
        'email': recipient_email,
        'arrival_date': request.form.get('arrival_date', 'N/A'),
        'departure_date': request.form.get('departure_date', 'N/A'),
        'duration': request.form.get('duration', 'N/A'),
        'travelers': request.form.get('travelers', '1'),
        'children': 'Yes' if request.form.get('children') else 'No',
        'places': request.form.get('places', 'N/A'),
        'travel_type': request.form.get('travel_type', 'N/A'),
        'vehicle': request.form.get('vehicle', 'N/A'),
        'notes': request.form.get('notes', '')
    }

    tourist_msg = Message(
        subject="Your Safari Booking Request - Pardalis Safari Tour",
        recipients=[booking_data['email']]
    )
    tourist_msg.body = (
        f"Dear {booking_data['first_name']},\n\n"
        f"Thank you for choosing Pardalis Safari Tour!\n\n"
        f"We have received your booking request for arrival on {booking_data['arrival_date']}. "
        f"Our travel specialists are reviewing your request and will contact you shortly with a personalized itinerary.\n\n"
        f"Best regards,\n"
        f"Pardalis Safari Tour Team"
    )

    try:
        mail.send(tourist_msg)
        logging.info("Tourist email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send tourist email: {e}")

    pdf_html = render_template('pdf_template.html', data=booking_data)
    pdf_file = generate_pdf(pdf_html)

    admin_msg = Message(
        subject=f"New Booking Request: {booking_data['first_name']} {booking_data['last_name']}",
        recipients=[ADMIN_EMAIL]
    )
    admin_msg.body = (
        f"A new safari request was submitted.\n\n"
        f"Client Name: {booking_data['first_name']} {booking_data['last_name']}\n"
        f"Email: {booking_data['email']}\n"
        f"Country: {booking_data['country']}\n\n"
        f"Please find the full booking summary attached as a PDF."
    )

    if pdf_file:
        admin_msg.attach(
            filename=f"Booking_{booking_data['last_name']}_{booking_data['first_name']}.pdf",
            content_type="application/pdf",
            data=pdf_file.getvalue()
        )

    try:
        mail.send(admin_msg)
        logging.info("Admin email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send admin email: {e}")

    return render_template(
        'thank_you.html',
        first_name=booking_data['first_name'],
        email=booking_data['email']
    )


# --- NAVIGATION PAGES ---

@app.route('/about')
def about():
    items = [
        {"title": "Our Team", "image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=600&q=80", "text": "Experienced local Tanzanian guide professionals and safari experts."},
        {"title": "Custom Fleet", "image": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?auto=format&fit=crop&w=600&q=80", "text": "Specially modified 4x4 Land Cruisers with pop-up roofs for optimal game viewing."},
        {"title": "Community Support", "image": "https://images.unsplash.com/photo-1484406566174-9da000fda645?auto=format&fit=crop&w=600&q=80", "text": "Giving back to local communities and supporting regional conservation initiatives."}
    ]
    return render_template_string(PAGE_TEMPLATE, title="About Us", heading="About Pardalis Safari Tours", subheading="Excellence, Safety, and Authentic Exploration", description="Learn more about our company background, expert team, and commitment to delivering unforgettable Tanzanian safaris.", items=items)


@app.route('/destinations')
def destinations():
    items = [
        {"title": "Serengeti National Park", "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=600&q=80", "text": "Home to the Great Wildebeest Migration and endless golden savannah plains.", "link": url_for('serengeti')},
        {"title": "Ngorongoro Crater", "image": "https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=600&q=80", "text": "A breathtaking UNESCO World Heritage site filled with dense wildlife populations.", "link": url_for('ngorongoro')},
        {"title": "Tarangire National Park", "image": "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=600&q=80", "text": "Renowned for massive elephant herds and majestic ancient baobab trees.", "link": url_for('tarangire')},
        {"title": "Zanzibar Beaches", "image": "https://images.unsplash.com/photo-1586861635167-e5223aadc9fe?auto=format&fit=crop&w=600&q=80", "text": "Pristine white sand beaches and clear turquoise waters of the Indian Ocean.", "link": url_for('zanzibar')}
    ]
    return render_template_string(PAGE_TEMPLATE, title="Destinations", heading="Tanzania Destinations", subheading="Explore Africa's Most Spectacular Wildlife Parks", description="Discover our top destination offerings across Tanzania's northern circuit and tropical islands.", items=items)


@app.route('/safaris')
def safaris():
    items = [
        {"title": "Classic Wildlife Safari", "image": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=600&q=80", "text": "Multi-day wildlife game drives through northern Tanzania's premier national parks.", "link": url_for('classic_wildlife')},
        {"title": "Great Migration Safaris", "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=600&q=80", "text": "Specialized seasonal itineraries tracking million-strong wildebeest and zebra herds.", "link": url_for('great_migration')},
        {"title": "Photographic Expeditions", "image": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?auto=format&fit=crop&w=600&q=80", "text": "Custom vehicle setups and timing designed specifically for wildlife photographers.", "link": url_for('photographic_expeditions')}
    ]
    return render_template_string(PAGE_TEMPLATE, title="Safaris", heading="Safari Packages", subheading="Tailor-Made Big Five Adventures", description="Choose from our wide range of curated safari packages crafted for all types of travelers.", items=items)


@app.route('/climbing-trekking')
def climbing_trekking():
    items = [
        {
            "title": "Mount Kilimanjaro Climbs",
            "image": "https://images.unsplash.com/photo-1650668302197-7f556c34cb91?auto=format&fit=crop&w=600&q=80",
            "text": "Guided treks to Uhuru Peak via Machame, Lemosho, and Marangu routes.",
            "link": url_for('kilimanjaro_detail')
        },
        {
            "title": "Mount Meru Treks",
            "image": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=600&q=80",
            "text": "Scenic multi-day trekking ideal for acclimatization and panoramic views.",
            "link": url_for('meru_detail')
        },
        {
            "title": "Ol Doinyo Lengai",
            "image": "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=600&q=80",
            "text": "Challenging active volcano hikes located in the heart of Maasai land.",
            "link": url_for('lengai_detail')
        }
    ]
    return render_template_string(
        PAGE_TEMPLATE, 
        title="Climbing & Trekking", 
        heading="Mountain Climbing & Trekking", 
        subheading="Conquer Africa's Highest Peaks", 
        description="Professional mountain expeditions supported by certified guides, porters, and mountain cooks.", 
        items=items
    )


@app.route('/accommodation')
def accommodation():
    items = [
        {"title": "Luxury Tented Camps", "image": "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=600&q=80", "text": "Immerse yourself in nature without compromising on high-end comfort and fine dining."},
        {"title": "Safari Lodges", "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80", "text": "Full-service luxury lodges offering swimming pools, spa facilities, and epic park views."},
        {"title": "Beach Resorts", "image": "https://images.unsplash.com/photo-1586861635167-e5223aadc9fe?auto=format&fit=crop&w=600&q=80", "text": "Exclusive beachfront resorts in Zanzibar for post-safari relaxation."}
    ]
    return render_template_string(PAGE_TEMPLATE, title="Accommodation", heading="Lodges & Luxury Camps", subheading="Comfortable Lodging Under African Skies", description="We partner with carefully vetted lodges and camps to ensure rest, fine dining, and security throughout your journey.", items=items)


# --- DESTINATION DETAIL ROUTES ---

@app.route('/destinations/ngorongoro')
def ngorongoro():
    photos = [
        {"url": url_for('static', filename='images/menu/ngorongoro/about_the_ngoro_crater.webp'), "caption": "Maasai overlooking Ngorongoro Crater"},
        {"url": url_for('static', filename='images/menu/ngorongoro/animals.jpg'), "caption": "Abundant Wildlife at the Crater Floor"},
        {"url": url_for('static', filename='images/menu/ngorongoro/elephant.jpg'), "caption": "African Elephant in Ngorongoro"},
        {"url": url_for('static', filename='images/menu/ngorongoro/lion.jpg'), "caption": "Lioness Resting on Rocks"},
        {"url": url_for('static', filename='images/menu/ngorongoro/rhino.jpg'), "caption": "Rare Black Rhinoceros"},
        {"url": url_for('static', filename='images/menu/ngorongoro/zebra.jpg'), "caption": "Large Herd of Zebras"}
    ]
    video_url = "https://www.youtube.com/embed/eSUuVpnKQIE"
    return render_template('ngorongoro.html', photos=photos, video_url=video_url)


@app.route('/destinations/zanzibar')
def zanzibar():
    photos = [
        {"url": url_for('static', filename='images/menu/zanzibar/beaches.jpg'), "caption": "Aerial View of Pristine Zanzibar Coastline"},
        {"url": url_for('static', filename='images/menu/zanzibar/images (1).jpg'), "caption": "Traditional Dhow Sailing across Turquoise Waters"},
        {"url": url_for('static', filename='images/menu/zanzibar/images (2).jpg'), "caption": "Historic Stone Town Oceanfront View"},
        {"url": url_for('static', filename='images/menu/zanzibar/images.jpg'), "caption": "Luxury Oceanfront Resort & Tropical Palm Gardens"},
        {"url": url_for('static', filename='images/menu/zanzibar/island.jpg'), "caption": "The Famous Rock Restaurant on Coral Outcrop"},
        {"url": url_for('static', filename='images/menu/zanzibar/istock-2149024822_banner.jpg'), "caption": "Powder-White Sand Shorelines & Azure Lagoon"},
        {"url": url_for('static', filename='images/menu/zanzibar/natures.jpg'), "caption": "Private Tropical Sandbank & Coral Atoll"},
        {"url": url_for('static', filename='images/menu/zanzibar/zanzibar images.jpg'), "caption": "Swimming in Natural Crystal-Clear Cave Lagoon"}
    ]
    video_url = "https://www.instagram.com/reel/DbVK_MCP1pG/embed"
    return render_template('zanzibar.html', photos=photos, video_url=video_url)


@app.route('/destinations/serengeti')
def serengeti():
    photos = [
        {"url": url_for('static', filename='images/menu/serengeti/A_Tower_of_Giraffes_in_The_Serengeti.jpg'), "caption": "Towering Giraffes Across the Acacia Savanna"},
        {"url": url_for('static', filename='images/menu/serengeti/leopard.jpg'), "caption": "Solitary Leopard Resting on an Acacia Branch"},
        {"url": url_for('static', filename='images/menu/serengeti/masai in serengeti.jpg'), "caption": "Traditional Maasai Cultural Village Experience"},
        {"url": url_for('static', filename='images/menu/serengeti/migration.jpg'), "caption": "Dramatic River Crossing During the Great Migration"},
        {"url": url_for('static', filename='images/menu/serengeti/morning in serengeti.jpg'), "caption": "Breathtaking Serengeti Sunrise & Acacia Silhouette"},
        {"url": url_for('static', filename='images/menu/serengeti/safari in serengeti.jpg'), "caption": "Custom 4x4 Safari Land Cruiser Among Wildlife"},
        {"url": url_for('static', filename='images/menu/serengeti/serengeti welbest.jpg'), "caption": "Great Wildebeest Migration Across Endless Plains"}
    ]
    video_url = "https://www.youtube.com/embed/UOr7wlJItPo"
    return render_template('serengeti.html', photos=photos, video_url=video_url)


@app.route('/destinations/tarangire')
def tarangire():
    photos = [
        {"url": url_for('static', filename='images/menu/tarangire/Bird-watching-in-Tarangire-national-park.jpg'), "caption": "Lilac-Breasted Roller"},
        {"url": url_for('static', filename='images/menu/tarangire/boabab-tarangire-national-park.jpg'), "caption": "Giant Baobab Tree"},
        {"url": url_for('static', filename='images/menu/tarangire/elephant in tarangire.jpg'), "caption": "Elephant Herd"},
        {"url": url_for('static', filename='images/menu/tarangire/map-of-tarangire-National-park.jpg'), "caption": "Tarangire Route Map"},
        {"url": url_for('static', filename='images/menu/tarangire/movement.jpg'), "caption": "Elephant Migration"},
        {"url": url_for('static', filename='images/menu/tarangire/nature in tarangire.jpg'), "caption": "River Valley Landscape"},
        {"url": url_for('static', filename='images/menu/tarangire/road trip.jpg'), "caption": "Giraffes & Safari Trail"},
        {"url": url_for('static', filename='images/menu/tarangire/safari.jpg'), "caption": "4x4 Safari Drive"},
        {"url": url_for('static', filename='images/menu/tarangire/weldlife.jpg'), "caption": "Tree-Climbing Lioness"}
    ]
    video_url = "https://www.youtube.com/embed/fLzxlms-PWo"
    return render_template('tarangire.html', photos=photos, video_url=video_url)


# --- INDIVIDUAL TREKKING DETAIL ROUTES ---

@app.route('/climbing-trekking/kilimanjaro')
def kilimanjaro_detail():
    photos = [
        {"url": url_for('static', filename='images/menu/mount kilimanjaro/mt_kilimanjaro (1).jpg'), "caption": "Snow-Capped Uhuru Peak View"},
        {"url": url_for('static', filename='images/menu/mount kilimanjaro/mt_kilimanjaro (2).jpg'), "caption": "Majestic Kilimanjaro Landscape"},
        {"url": url_for('static', filename='images/menu/mount kilimanjaro/mt_kilimanjaro.jpg'), "caption": "Climbers Trekking the Mountain Path"},
        {"url": url_for('static', filename='images/menu/mount kilimanjaro/mt_kilimanjaro4.jpg'), "caption": "Rocky Terrain Near High Altitude Camps"},
        {"url": url_for('static', filename='images/menu/mount kilimanjaro/mt_kilimanjaro5.jpg'), "caption": "Scenic Alpine Meadow Trail"},
        {"url": url_for('static', filename='images/menu/mount kilimanjaro/mt_kilimanjaro6.jpg'), "caption": "Celebration at Uhuru Peak (5895m)"}
    ]
    video_url = "https://www.youtube.com/embed/eSUuVpnKQIE"
    return render_template('kilimanjaro.html', photos=photos, video_url=video_url)

@app.route('/climbing-trekking/mount-meru')
def meru_detail():
    photos = [
        {"url": url_for('static', filename='images/mount meru/mountMeru1.jpg'), "caption": "Miriakamba Huts"},
        {"url": url_for('static', filename='images/mount meru/mountMeru2.jpg'), "caption": "View of Mount Meru Crater"},
        {"url": url_for('static', filename='images/mount meru/mountMeru3.jpg'), "caption": "Mount Meru Ridge"},
        {"url": url_for('static', filename='images/mount meru/mountMeru4.jpg'), "caption": "Volcanic Slopes"}
    ]
    video_url = "https://www.youtube.com/embed/eSUuVpnKQIE"
    return render_template('mount_meru.html', photos=photos, video_url=video_url)

@app.route('/climbing-trekking/ol-doinyo-lengai')
def lengai_detail():
    photos = [
        {"url": url_for('static', filename='images/oldonyo lengai/Oldonyo-Lengai.jpg'), "caption": "Ol Doinyo Lengai Volcanic Peak"},
        {"url": url_for('static', filename='images/oldonyo lengai/DSC_8562-Medium-1024x685.jpg'), "caption": "Maasai Guide overlooking the Valley"},
        {"url": url_for('static', filename='images/oldonyo lengai/Oldonyo-Lengai-1-1024x680.jpg'), "caption": "Volcanic Cone and Surrounding Plains"},
        {"url": url_for('static', filename='images/oldonyo lengai/Oldonyo-Lengai-3-1024x680.jpg'), "caption": "Scenery at the Base of the Mountain"}
    ]
    video_url = "https://www.youtube.com/embed/eSUuVpnKQIE"
    return render_template('ol_doinyo_lengai.html', photos=photos, video_url=video_url)

@app.route('/safaris/classic-wildlife')
def classic_wildlife():
    photos = [
        {"url": url_for('static', filename='images/menu/safari/classic1.jpg'), "caption": "Game Drives Across Northern Tanzania"},
        {"url": url_for('static', filename='images/menu/safari/classic2.jpg'), "caption": "Big Five Spotting in Ngorongoro Crater"},
        {"url": url_for('static', filename='images/menu/safari/classic3.jpg'), "caption": "Luxury Bush Camp Experience"}
    ]
    return render_template('classic_wildlife.html', photos=photos)

@app.route('/safaris/great-migration')
def great_migration():
    photos = [
        {"url": url_for('static', filename='images/menu/safari/migration1.jpg'), "caption": "Mara River Crossing Action"},
        {"url": url_for('static', filename='images/menu/safari/migration2.jpg'), "caption": "Herds Moving Across Serengeti Plains"},
        {"url": url_for('static', filename='images/menu/safari/migration3.jpg'), "caption": "Calving Season in Ndutu"}
    ]
    return render_template('great_migration.html', photos=photos)

@app.route('/safaris/photographic-expeditions')
def photographic_expeditions():
    photos = [
        {"url": url_for('static', filename='images/menu/safari/photo1.jpg'), "caption": "Golden Hour Wildlife Photography"},
        {"url": url_for('static', filename='images/menu/safari/photo2.jpg'), "caption": "4x4 Vehicle Equipped with Camera Mounts"},
        {"url": url_for('static', filename='images/menu/safari/photo3.jpg'), "caption": "Close-Up Predator Sightings"}
    ]
    return render_template('photographic_expeditions.html', photos=photos)

from flask import render_template, request, flash, redirect, url_for

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you can save to a database or send an automated email notification
        flash('Thank you for reaching out! We will get back to you shortly.', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)