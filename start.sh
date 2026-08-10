#!/bin/bash
# 1. पहले से चल रहे सभी अधूरे कंटेनर्स और नेटवर्क क्लैशेस को पूरी तरह साफ़ करो
sudo docker stop garud-perimeter garud-shield 2>/dev/null; sudo docker rm garud-perimeter garud-shield 2>/dev/null
sudo docker network rm garud-net 2>/dev/null; sudo docker network create garud-net 2>/dev/null

# 2. भीतरी कोर (Shield) को बिना किसी होस्ट नेटवर्क के, सिर्फ अंदरूनी 'garud-net' नेटवर्क पर पोर्ट 80 पर सुरक्षित चलाओ
sudo docker run -d --name garud-shield --network garud-net -v ~/garud_core/templates:/app/templates --env-file ~/garud_core/.env garud-shield

# 3. अब बाहरी पेरीमीटर को सीधे गेट पोर्ट 80 पर लाइव करो और अंदरूनी ऐप का टारगेट 'garud-shield:80' पर सिंक कर दो
sudo docker run -d -p 80:80 --name garud-perimeter --network garud-net -e TARGET_INTERNAL_APP="http://garud-shield:80" --env-file ~/garud_core/.env garud-perimeter
