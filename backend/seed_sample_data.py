# backend/seed_sample_data.py
"""
Script to populate the technique library with sample data
Run this from the backend directory: python seed_sample_data.py
"""

import sys
import os
from datetime import datetime

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def seed_sample_techniques():
    """Add sample techniques to the database"""
    
    app = create_app()
    
    with app.app_context():
        # Get the database instance and models from the app
        from app import db
        TechniqueLibrary = app.TechniqueLibrary
        
        # Sample techniques data based on BlackBeltWiki structure
        sample_techniques = [
            {
                'name': 'Front Kick (Mae Geri)',
                'style': 'Karate',
                'category': 'Kicks',
                'difficulty_level': 3,
                'belt_level': 'White Belt',
                'description': 'The front kick is one of the most fundamental kicks in karate. It is a linear attack that uses the ball of the foot to strike the target. This kick is excellent for creating distance between you and an opponent and can be used both defensively and offensively.',
                'instructions': '1. Start in a fighting stance with your guard up\n2. Lift your knee up toward your chest\n3. Extend your leg straight forward\n4. Strike with the ball of your foot\n5. Quickly retract your leg back to the chambered position\n6. Return to fighting stance',
                'tips': 'Keep your balance on your supporting leg. Pull your toes back to expose the ball of your foot. Practice slowly at first to develop proper form.',
                'variations': '• Front snap kick - quick snapping motion\n• Front thrust kick - pushing motion for distance\n• High front kick - targeting the head\n• Low front kick - targeting the legs',
                'source_url': 'https://blackbeltwiki.com/front-kick',
                'tags': ['basic', 'linear', 'karate', 'striking']
            },
            {
                'name': 'Roundhouse Kick (Mawashi Geri)',
                'style': 'Karate',
                'category': 'Kicks',
                'difficulty_level': 5,
                'belt_level': 'Yellow Belt',
                'description': 'The roundhouse kick is a circular kick that strikes with the instep or shin. It is one of the most versatile kicks in martial arts and can target multiple levels of the body.',
                'instructions': '1. Start in fighting stance\n2. Pivot on your supporting foot\n3. Lift your knee to the side\n4. Snap your leg in a circular motion\n5. Strike with the instep or shin\n6. Follow through and return to stance',
                'tips': 'Pivot completely on your supporting foot. Keep your hands up for balance. Practice hitting different target levels.',
                'variations': '• Low roundhouse - targeting legs\n• Mid roundhouse - targeting body\n• High roundhouse - targeting head\n• Switch roundhouse - changing stance',
                'source_url': 'https://blackbeltwiki.com/roundhouse-kick',
                'tags': ['intermediate', 'circular', 'karate', 'versatile']
            },
            {
                'name': 'Side Kick (Yoko Geri)',
                'style': 'Karate',
                'category': 'Kicks',
                'difficulty_level': 6,
                'belt_level': 'Orange Belt',
                'description': 'The side kick is a powerful lateral kick that uses the heel or blade of the foot. It generates tremendous power and is excellent for stopping an advancing opponent.',
                'instructions': '1. Start in fighting stance\n2. Lift your knee up toward your chest\n3. Turn your hip over and extend leg sideways\n4. Strike with the heel or blade of foot\n5. Keep your body aligned\n6. Retract and return to stance',
                'tips': 'Turn your hip completely over. Keep your supporting leg strong. Lean slightly away from the kick for balance.',
                'variations': '• Side snap kick - quick snapping motion\n• Side thrust kick - pushing motion\n• Jumping side kick - with a jump\n• Spinning side kick - with rotation',
                'source_url': 'https://blackbeltwiki.com/side-kick',
                'tags': ['intermediate', 'lateral', 'powerful', 'karate']
            },
            {
                'name': 'Jab',
                'style': 'Boxing',
                'category': 'Punches',
                'difficulty_level': 2,
                'belt_level': 'Beginner',
                'description': 'The jab is the most fundamental punch in boxing. It is a quick, straight punch thrown with the lead hand. It is used for distance, timing, and setting up other techniques.',
                'instructions': '1. Start in boxing stance\n2. Extend your lead hand straight forward\n3. Rotate your fist so palm faces down\n4. Step forward slightly with lead foot\n5. Snap the punch out and back quickly\n6. Keep your guard up',
                'tips': 'Keep it quick and snappy. Don\'t telegraph the punch. Use it to gauge distance and set up combinations.',
                'variations': '• Power jab - with more force\n• Flicker jab - very fast and light\n• Step jab - with forward step\n• Double jab - two quick jabs',
                'source_url': 'https://blackbeltwiki.com/jab',
                'tags': ['basic', 'boxing', 'fundamental', 'speed']
            },
            {
                'name': 'Cross Punch',
                'style': 'Boxing',
                'category': 'Punches',
                'difficulty_level': 3,
                'belt_level': 'Beginner',
                'description': 'The cross is a power punch thrown with the rear hand. It travels in a straight line across the body and generates power from hip rotation and weight transfer.',
                'instructions': '1. Start in boxing stance\n2. Rotate your hips and shoulders\n3. Drive off your back foot\n4. Extend rear hand straight forward\n5. Rotate fist palm down on impact\n6. Return to guard position',
                'tips': 'Generate power from your legs and hips. Keep your lead hand up for protection. Follow through with your shoulder.',
                'variations': '• Overhand cross - slightly downward angle\n• Counter cross - as a counter attack\n• Body cross - targeting the body\n• Step cross - with forward step',
                'source_url': 'https://blackbeltwiki.com/cross-punch',
                'tags': ['basic', 'boxing', 'power', 'fundamental']
            },
            {
                'name': 'High Block (Age Uke)',
                'style': 'Karate',
                'category': 'Blocks',
                'difficulty_level': 2,
                'belt_level': 'White Belt',
                'description': 'The high block is used to defend against attacks to the head and upper body. It deflects incoming strikes upward and away from the target area.',
                'instructions': '1. Start with your blocking arm across your body\n2. Sweep your arm upward and outward\n3. End with your forearm above your forehead\n4. Keep your elbow bent at about 90 degrees\n5. Your fist should be about one fist-width from your head',
                'tips': 'Block with the outer edge of your forearm. Don\'t just raise your arm - sweep it upward. Keep your other hand in guard position.',
                'variations': '• Rising block - with upward motion\n• X-block - using both arms\n• Augmented block - with supporting hand\n• Knife hand block - using open hand',
                'source_url': 'https://blackbeltwiki.com/high-block',
                'tags': ['basic', 'defense', 'karate', 'fundamental']
            },
            {
                'name': 'Hip Throw (O Goshi)',
                'style': 'Judo',
                'category': 'Throws',
                'difficulty_level': 7,
                'belt_level': 'Yellow Belt',
                'description': 'The hip throw is a fundamental throw in judo that uses hip positioning and leverage to throw an opponent. It teaches the basic principles of using your body as a fulcrum.',
                'instructions': '1. Establish a proper grip on your opponent\n2. Step in close with your right foot\n3. Turn your body and place your hip under opponent\n4. Wrap your right arm around their waist\n5. Lift and rotate using your hips\n6. Follow through to complete the throw',
                'tips': 'Get your hip lower than your opponent\'s center of gravity. Use your legs to lift, not just your arms. Practice the turning motion slowly.',
                'variations': '• Small hip throw - with less contact\n• Large hip throw - with more contact\n• Floating hip throw - timing variation\n• Counter hip throw - as a counter',
                'source_url': 'https://blackbeltwiki.com/hip-throw',
                'tags': ['intermediate', 'judo', 'grappling', 'leverage']
            },
            {
                'name': 'Double Leg Takedown',
                'style': 'Wrestling',
                'category': 'Throws',
                'difficulty_level': 6,
                'belt_level': 'Intermediate',
                'description': 'The double leg takedown is a fundamental wrestling technique used to take an opponent to the ground by attacking both legs simultaneously.',
                'instructions': '1. Change levels by dropping your stance\n2. Step forward with your lead foot\n3. Drive your shoulder into opponent\'s hips\n4. Wrap both arms around both legs\n5. Lift and drive forward\n6. Follow through to the ground',
                'tips': 'Change levels before moving forward. Keep your head up and to one side. Drive through with your legs.',
                'variations': '• High double leg - higher grip\n• Low double leg - lower grip\n• Blast double - explosive entry\n• Outside step double - step outside',
                'source_url': 'https://blackbeltwiki.com/double-leg-takedown',
                'tags': ['intermediate', 'wrestling', 'takedown', 'aggressive']
            },
            {
                'name': 'Spinning Hook Kick',
                'style': 'Taekwondo',
                'category': 'Kicks',
                'difficulty_level': 8,
                'belt_level': 'Black Belt',
                'description': 'The spinning hook kick is an advanced technique that combines rotation with a hooking motion. It generates tremendous power and can be used to attack from unexpected angles.',
                'instructions': '1. Start in fighting stance\n2. Begin spinning by turning away from target\n3. Lift your leg as you complete the spin\n4. Hook your leg around to strike the target\n5. Strike with the heel or back of foot\n6. Follow through and recover balance',
                'tips': 'Maintain balance throughout the spin. Keep your eyes on the target as long as possible. Practice the timing of the hook motion.',
                'variations': '• High spinning hook - targeting head\n• Low spinning hook - targeting legs\n• Jumping spinning hook - with jump\n• Counter spinning hook - as counter',
                'source_url': 'https://blackbeltwiki.com/spinning-hook-kick',
                'tags': ['advanced', 'taekwondo', 'spinning', 'powerful']
            },
            {
                'name': 'Triangle Choke',
                'style': 'Brazilian Jiu-Jitsu',
                'category': 'Submissions',
                'difficulty_level': 7,
                'belt_level': 'Blue Belt',
                'description': 'The triangle choke is a submission technique that uses the legs to create a chokehold around the opponent\'s neck and arm. It\'s one of the most effective submissions in BJJ.',
                'instructions': '1. Control opponent from guard position\n2. Break their posture and pull them forward\n3. Throw one leg over their shoulder\n4. Lock your legs around their neck and arm\n5. Adjust the angle and squeeze\n6. Apply pressure until tap or sleep',
                'tips': 'Break their posture first. Get the angle right before finishing. Cut the angle to tighten the choke.',
                'variations': '• Mounted triangle - from mount\n• Inverted triangle - upside down\n• Arm triangle - using arms\n• Triangle from guard - classic setup',
                'source_url': 'https://blackbeltwiki.com/triangle-choke',
                'tags': ['advanced', 'bjj', 'submission', 'chokehold']
            },
            {
                'name': 'Basic Stance (Heiko Dachi)',
                'style': 'Karate',
                'category': 'Stances',
                'difficulty_level': 1,
                'belt_level': 'White Belt',
                'description': 'The basic parallel stance is the foundation of all karate techniques. It teaches proper posture, balance, and weight distribution.',
                'instructions': '1. Stand with feet parallel\n2. Feet should be shoulder-width apart\n3. Distribute weight evenly on both feet\n4. Keep your back straight\n5. Relax your shoulders\n6. Look straight ahead',
                'tips': 'Keep your center of gravity low. Don\'t lock your knees. Maintain natural breathing.',
                'variations': '• Natural stance - relaxed position\n• Attention stance - formal position\n• Ready stance - prepared position\n• Meditation stance - for focus',
                'source_url': 'https://blackbeltwiki.com/basic-stance',
                'tags': ['basic', 'fundamental', 'karate', 'foundation']
            },
            {
                'name': 'Uppercut',
                'style': 'Boxing',
                'category': 'Punches',
                'difficulty_level': 4,
                'belt_level': 'Intermediate',
                'description': 'The uppercut is a vertical punch that travels upward to strike the opponent\'s chin or solar plexus. It\'s particularly effective at close range.',
                'instructions': '1. Start in boxing stance\n2. Drop your punching hand slightly\n3. Bend your knees and lower your body\n4. Drive upward with your legs\n5. Punch in a vertical arc\n6. Rotate your fist palm toward you',
                'tips': 'Generate power from your legs. Keep the punch compact. Don\'t drop your hand too low before punching.',
                'variations': '• Lead uppercut - with front hand\n• Rear uppercut - with back hand\n• Body uppercut - targeting body\n• Shovel hook - hybrid technique',
                'source_url': 'https://blackbeltwiki.com/uppercut',
                'tags': ['intermediate', 'boxing', 'close-range', 'vertical']
            },
            {
                'name': 'Forward Roll (Mae Ukemi)',
                'style': 'Judo',
                'category': 'Breakfalls',
                'difficulty_level': 4,
                'belt_level': 'Yellow Belt',
                'description': 'The forward roll is a fundamental breakfall technique that allows you to safely absorb impact when thrown forward. It\'s essential for safe practice.',
                'instructions': '1. Start in a crouched position\n2. Place one hand on the ground\n3. Tuck your chin to your chest\n4. Roll diagonally across your back\n5. Use your opposite hand to slap the mat\n6. Return to standing position',
                'tips': 'Never roll straight over your spine. Keep your chin tucked. Practice on soft surfaces first.',
                'variations': '• High forward roll - from standing\n• Low forward roll - from crouch\n• Running forward roll - with momentum\n• Silent forward roll - without slapping',
                'source_url': 'https://blackbeltwiki.com/forward-roll',
                'tags': ['safety', 'judo', 'fundamental', 'breakfall']
            },
            {
                'name': 'Knife Hand Strike (Shuto Uchi)',
                'style': 'Karate',
                'category': 'Strikes',
                'difficulty_level': 5,
                'belt_level': 'Green Belt',
                'description': 'The knife hand strike, also known as the karate chop, uses the outer edge of the hand to strike. It can be very effective against soft targets.',
                'instructions': '1. Form your hand into a blade shape\n2. Keep your fingers straight and together\n3. Bend your thumb against your palm\n4. Strike with the outer edge of your hand\n5. Keep your wrist straight and strong\n6. Follow through the target',
                'tips': 'Condition your hands gradually. Target soft areas like the neck or ribs. Keep your hand rigid on impact.',
                'variations': '• Inward knife hand - horizontal strike\n• Outward knife hand - reverse direction\n• Downward knife hand - vertical strike\n• Rising knife hand - upward motion',
                'source_url': 'https://blackbeltwiki.com/knife-hand-strike',
                'tags': ['intermediate', 'karate', 'precision', 'traditional']
            },
            {
                'name': 'Sprawl',
                'style': 'Wrestling',
                'category': 'Defense',
                'difficulty_level': 5,
                'belt_level': 'Intermediate',
                'description': 'The sprawl is a defensive technique used to avoid takedown attempts. It involves quickly moving your legs back while dropping your hips to the ground.',
                'instructions': '1. React immediately to takedown attempt\n2. Throw your legs back quickly\n3. Drop your hips to the ground\n4. Spread your legs wide for base\n5. Put your weight on opponent\'s shoulders\n6. Work to improve position',
                'tips': 'React as fast as possible. Get your hips down and back. Use your weight to pressure opponent.',
                'variations': '• Sprawl and brawl - with striking\n• Hip heist - transitional movement\n• Sprawl to turtle - defensive position\n• Sprawl to submission - offensive follow-up',
                'source_url': 'https://blackbeltwiki.com/sprawl',
                'tags': ['defense', 'wrestling', 'reactive', 'fundamental']
            }
        ]
        
        print("🌱 Seeding sample technique data...")
        
        imported_count = 0
        updated_count = 0
        
        for technique_data in sample_techniques:
            # Check if technique already exists
            existing = TechniqueLibrary.query.filter_by(name=technique_data['name']).first()
            
            if existing:
                print(f"⏭️  Technique already exists: {technique_data['name']}")
                updated_count += 1
            else:
                # Create new technique
                technique = TechniqueLibrary(
                    name=technique_data['name'],
                    style=technique_data['style'],
                    category=technique_data['category'],
                    difficulty_level=technique_data['difficulty_level'],
                    belt_level=technique_data['belt_level'],
                    description=technique_data['description'],
                    instructions=technique_data['instructions'],
                    tips=technique_data['tips'],
                    variations=technique_data['variations'],
                    source_url=technique_data['source_url'],
                    source_site='BlackBeltWiki',
                    tags=technique_data['tags'],
                    view_count=0,
                    bookmark_count=0
                )
                
                db.session.add(technique)
                imported_count += 1
                print(f"✅ Added: {technique_data['name']} ({technique_data['style']})")
        
        try:
            db.session.commit()
            print(f"\n📊 Seeding Complete!")
            print(f"   ✅ Imported: {imported_count}")
            print(f"   ⏭️  Already existed: {updated_count}")
            print(f"   📚 Total techniques in database: {TechniqueLibrary.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving to database: {str(e)}")
            raise e

def seed_categories():
    """Add sample categories to the database"""
    app = create_app()
    
    with app.app_context():
        # Get the database instance and models from the app
        from app import db
        TechniqueCategory = app.TechniqueCategory
        
        categories = [
            {'name': 'Kicks', 'description': 'Leg-based striking techniques'},
            {'name': 'Punches', 'description': 'Hand-based striking techniques'},
            {'name': 'Strikes', 'description': 'Various striking techniques'},
            {'name': 'Blocks', 'description': 'Defensive techniques'},
            {'name': 'Throws', 'description': 'Grappling techniques to take opponent down'},
            {'name': 'Submissions', 'description': 'Joint locks and chokes'},
            {'name': 'Stances', 'description': 'Foundation positions'},
            {'name': 'Breakfalls', 'description': 'Safety techniques for falling'},
            {'name': 'Defense', 'description': 'Defensive techniques and counters'}
        ]
        
        print("🏷️  Seeding categories...")
        
        for cat_data in categories:
            existing = TechniqueCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = TechniqueCategory(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                print(f"✅ Added category: {cat_data['name']}")
        
        db.session.commit()
        print("🏷️  Categories seeded successfully!")

if __name__ == '__main__':
    print("🌱 Starting database seeding...")
    print("🗄️  This will add sample martial arts techniques to your database")
    
    try:
        seed_categories()
        seed_sample_techniques()
        print("\n🎉 Database seeding completed successfully!")
        print("🔗 You can now test the technique library at http://localhost:3000/techniques")
    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)