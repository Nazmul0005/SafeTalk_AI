EXPLICIT_PATTERNS = [
    r'\b(fuck|fucking|(fucked)(?! up))\b(?=.*\b(sex|sexual|explicit)\b)(?!.*\b(biology|education|class|lesson|medical|health|art|exhibit|book|story|poem|novel|game|movie|film|idiom|metaphor|reproduction)\b)',
    r'\b((pussy)(?! cat)|dick|cock|penis|vagina)\b(?=.*\b(sex|sexual|explicit)\b)(?!.*\b(biology|education|class|lesson|medical|health|art|exhibit|book|story|poem|novel|game|movie|film|animal|pet)\b)',
    r'\b(cum|cumming|orgasm)\b(?=.*\b(sex|sexual|explicit)\b)(?!.*\b(biology|education|class|lesson|medical|health|art|exhibit|book|story|poem|novel|game|movie|film|joy|metaphor)\b)',
    r'\b(horny|wet|hard|erect)\b(?=.*\b(sex|sexual|aroused)\b)(?!.*\b(biology|education|class|lesson|medical|health|art|exhibit|book|story|poem|novel|game|movie|film|weather|rain|ground|anger|metaphor)\b)',
    r'\b(69)\b(?=.*\b(sex|position|sexual)\b)(?!.*\b(biology|education|class|lesson|medical|health|art|exhibit|book|story|poem|novel|game|movie|film|number|math|yoga)\b)',
    r'\b(suck|lick|taste|swallow)\b.*\b(you|me|it)\b(?=.*\b(sex|sexual|genital|erotic)\b)(?!.*\b(food|drink|candy|meal|lollipop|story|game)\b)',
    r'\b(naked|nude|undress|strip)\b(?=.*\b(sex|sexual|erotic|bedroom)\b)(?!.*\b(paint|art|sculpture|wall|baby|bath|child|family|medical|health|exhibit|book|story|poem|novel|game|movie|film)\b)',
    r'\b(bedroom|bed|shower|bath)\b.*\b(together|with me|with you)\b(?=.*\b(sex|sexual|intimate|romantic)\b)(?!.*\b(family|child|baby|friend|dinner|movie|game|event|party|health|medical)\b)',
    r'\b(kiss|touch|feel|grab)\b.*\b(body|skin|lips|neck)\b(?=.*\b(sex|sexual|erotic|romantic)\b)(?!.*\b(baby|child|friend|family|medical|health|story|poem|novel|game|movie|film)\b)',
    r'\bhow far.*\b(down|up|deep)\b(?=.*\b(sex|sexual|bed|intimate)\b)(?!.*\b(road|path|distance|map|travel|story|game|book|novel|movie|film)\b)',
    r'\bslowly.*\b(kiss|touch|lick)\b(?=.*\b(sex|sexual|erotic|romantic)\b)(?!.*\b(story|poem|novel|game|movie|film|frog|list|options)\b)',
    r'\bmake.*\b(love|out|you moan)\b(?=.*\b(sex|sexual|bed|intimate)\b)(?!.*\b(potion|game|story|poem|novel|movie|film|fun)\b)',
    r'\b(desire|want|need).*\b(you|your body)\b(?=.*\b(sex|sexual|erotic|romantic)\b)(?!.*\b(success|help|support|friendship|novel|book|story|poem|game|movie|film)\b)',
    r'\b(turn.*on|turned on|aroused)\b(?=.*\b(sex|sexual|erotic)\b)(?!.*\b(light|switch|lamp|anger|art|exhibit|book|story|poem|novel|game|movie|film)\b)',
    r'\b(dirty|naughty|bad).*\b(things|thoughts|ideas)\b(?=.*\b(sex|sexual|erotic)\b)(?!.*\b(clean|joke|fun|cleaning|house|metaphor)\b)',
]

SUGGESTIVE_CONTEXT_PATTERNS = [
    r'\btonight.*\bwant\b(?=.*\b(sex|sexual|date|intimate)\b)(?!.*\b(event|party|dinner|movie|film|game|conversation|friendship|book|story|poem|novel)\b)',
    r'\bquestion.*\bhow far\b(?=.*\b(sex|sexual|bed|intimate)\b)(?!.*\b(road|path|distance|map|travel|space|book|story|game|movie|film)\b)',
    r'\bslowly.*\bkiss.*\bdown\b(?=.*\b(sex|sexual|erotic|romantic)\b)(?!.*\b(list|options|story|poem|novel|game|movie|film)\b)',
    r'\bfrom.*\blips.*\bdown\b(?=.*\b(sex|sexual|erotic|romantic)\b)(?!.*\b(toes|poem|story|novel|book|game|movie|film)\b)',
    r'\bcan\'t wait.*\bsee.*\bwearing\b(?=.*\b(underwear|lingerie|naked|nude)\b)(?!.*\b(costume|dress|outfit|shirt|party|event|game|movie|film)\b)',
    r'\bwhat.*\bwearing.*\btonight\b(?=.*\b(underwear|lingerie|naked|nude)\b)(?!.*\b(costume|dress|outfit|shirt|movie|film|party|event|game)\b)',
    r'\bmeet.*\bprivate\b(?=.*\b(sex|sexual|date|romantic)\b)(?!.*\b(meeting|study|work|project|conversation|friendship|book|story|game|movie|film)\b)',
    r'\bcome over.*\btonight\b(?=.*\b(sex|sexual|date|intimate)\b)(?!.*\b(dinner|movie|party|game|conversation|friendship|event|book|story|novel|film)\b)',
]

HARASSMENT_PATTERNS = [  # Unchanged, as few false positives; already has good exclusions
    r'\bwhy.*won\'t.*\brespond\b(?=.*\b(text|message|chat|date)\b)(?!.*\b(email|work|project|assignment)\b)',
    r'\bignoring.*\bme\b(?=.*\b(text|message|chat|date)\b)(?!.*\b(work|project|job)\b)',
    r'\byou.*\b(bitch|slut|whore)\b',
    r'\bstupid.*\b(girl|woman|bitch)\b',
    r'\byou owe me\b(?=.*\b(date|sex|kiss|meet)\b)(?!.*\b(favor|coffee|lunch|help)\b)',
    r'\bafter.*\bpaid\b(?=.*\b(date|sex|kiss|meet)\b)(?!.*\b(meal|dinner|lunch|ticket)\b)',
]

BODY_SHAMING_PATTERNS = [
    # Weight-related: Added required negative context
    r'\b(fat|obese|chubby|overweight|chunky|heavy)\b.*\b(pig|cow|whale|elephant)\b',
    r'\byou.*\b(fat|obese|chubby|overweight|chunky|heavy)\b(?=.*\b(bad|ugly|gross|disgusting|shame)\b)(?!.*\b(healthy|happy|confident|cute|normal|fine|beautiful|medical|health|discussion)\b)',
    r'\bno\s+fatties\b',
    r'\b(lose|diet|gym)\b.*\bweight\b.*\b(need|should|must)\b(?!.*\b(health|doctor|medical|advice|suggestion)\b)',
    r'\btoo\b.*\b(fat|heavy|big|large)\b.*\bfor\b(?=.*\b(bad|ugly|gross|disgusting|shame)\b)(?!.*\b(health|comfort|style|fit|normal|fine)\b)',
    r'\b(skinny|thin|anorexic|skeleton|stick)\b.*\b(freak|weird|gross)\b(?=.*\b(bad|ugly|disgusting|shame)\b)(?!.*\b(art|drawing|figure|medical|health|discussion)\b)',
    # Appearance: Added exclusions for discussions
    r'(?=.*\b(you|your|she|her|he|his|person|girl|woman|man|boy)\b)(?!.*\b(art|sculpture|painting|design|statue|drawing|figure|joke|fun|style|discussion|book|story|movie|film)\b)\b(ugly|hideous|disgusting|gross|repulsive)\b.*\b(face|look|appearance)\b',
    r'\byou.*\b(ugly|hideous|disgusting|gross|repulsive)\b(?=.*\b(bad|shame|insult)\b)(?!.*\b(joke|fun|style|discussion|book|story|movie|film)\b)',
    r'\b(plastic|fake|artificial)\b.*\b(face|lips|boobs|ass)\b(?!.*\b(surgery|medical|procedure|discussion|health)\b)',
    r'\bwithout.*\bmakeup\b.*\b(ugly|gross|hideous)\b(?!.*\b(style|discussion|joke|fun|normal|fine|beautiful)\b)',
    r'\b(acne|pimples|zits)\b.*\b(face|gross|disgusting)\b(?!.*\b(medical|health|skincare|discussion|normal|teen|adolescent)\b)',
    # Body image: Added required negative and more exclusions
    r'\b(small|tiny|flat|saggy|droopy)\b.*\b(boobs|tits|chest|breasts)\b(?=.*\b(bad|ugly|gross|disgusting|unattractive|shame)\b)(?!.*\b(normal|fine|beautiful|attractive|healthy|medical|discussion)\b)',
    r'\b(big|huge|massive|enormous)\b.*\b(ass|butt|thighs|belly)\b(?=.*\b(bad|ugly|gross|disgusting|unattractive|shame)\b)(?!.*\b(strong|healthy|fit|normal|fine|beautiful|medical|discussion)\b)',
    r'\byour.*\b(body|figure)\b.*\b(disgusting|gross|ugly|horrible)\b(?!.*\b(joke|fun|style|discussion|book|story|movie|film)\b)',
    r'\b(cellulite|stretch marks|scars)\b.*\b(gross|disgusting|ugly)\b(?!.*\b(normal|fine|beautiful|healthy|medical|discussion)\b)',
    r'\bwould.*\blook.*\bbetter.*\bwith\b.*\b(surgery|implants|reduction)\b(?!.*\b(medical|health|advice|discussion)\b)',
    # Lookism: Added exclusions for neutral contexts
    r'\bout.*of.*your.*league\b(?!.*\b(joke|fun|game|sports|discussion)\b)',
    r'\btoo.*\b(pretty|hot|attractive)\b.*\bfor.*you\b(?!.*\b(joke|fun|him|her|discussion)\b)',
    r'\bnot.*\b(pretty|attractive|hot)\b.*\benough\b(?!.*\b(role|job|discussion|joke|fun)\b)',
    r'\b(standards|deserve)\b.*\bbetter.*\blooking\b(?!.*\b(friends|joke|fun|discussion)\b)',
    r'\byou.*\blook.*like\b.*\b(man|dude|boy)\b(?=.*\b(woman|girl|female)\b)(?!.*\b(joke|fun|style|discussion|costume)\b)',
    r'\b(masculine|manly)\b.*\b(face|features|jaw)\b(?=.*\b(woman|girl|female)\b)(?!.*\b(joke|fun|style|discussion|art)\b)',
    # Age/height: Unchanged or minor additions, as fewer issues
    r'\b(old|ancient|wrinkled|aged)\b.*\b(hag|crone|grandma)\b',
    r'\btoo.*\bold\b.*\bfor\b(?!.*\b(job|role|work|experience|discussion)\b)',
    r'\b(young|immature|childish)\b.*\blooking\b(?!.*\b(cute|adorable|charming|normal|discussion)\b)',
    r'\btoo.*\b(short|tall|small|big)\b.*\bfor\b(?!.*\b(sport|game|style|fit|basketball|gymnastics|athletics|running|jumping|swimming|discussion)\b)',
    r'\b(midget|dwarf|giant|amazon)\b',
    r'\bshort.*\b(guy|man)\b.*\b(complex|syndrome)\b',
]

# Emotional abuse and manipulation patterns (unchanged, as no false positives identified)
EMOTIONAL_ABUSE_PATTERNS = [
    r'\byou\'re\s+(crazy|insane|mental|psycho|delusional)\b(?=.*\b(lie|wrong|fake|gaslight|manipulate)\b)(?!.*\b(love|like|fan|happy|excited)\b)',
    r'\bthat\s+(never|didn\'t)\s+happen(ed)?\b(?=.*\b(lie|deny|gaslight)\b)(?!.*\b(mistake|misunderstand|confusion)\b)',
    r'\byou\'re\s+(imagining|making)\s+(it|things)\s+up\b(?=.*\b(lie|gaslight|manipulate)\b)',
    r'\byou\'re\s+being\s+(dramatic|paranoid|irrational)\b(?=.*\b(manipulate|control|gaslight)\b)(?!.*\b(joke|fun|play)\b)',
    r'\bi\s+never\s+said\s+that\b(?=.*\b(lie|deny|gaslight)\b)(?!.*\b(misunderstand|mistake|clarify)\b)',
    r'\byou\'re\s+remembering\s+(it\s+)?wrong\b(?=.*\b(lie|gaslight|manipulate)\b)',
    r'\byou\'re\s+overreacting\b(?=.*\b(manipulate|control|gaslight)\b)(?!.*\b(joke|calm|fun|play)\b)',
    r'\bif\s+you\s+(loved|cared\s+about)\s+me\s+you\s+would\b(?=.*\b(pressure|force|demand|manipulate)\b)(?!.*\b(help|support|call|visit|party)\b)',
    r'\bif\s+you\s+don\'t.*i\'ll\s+(leave|break\s+up)\b(?=.*\b(threat|force|manipulate)\b)',
    r'\bafter\s+everything\s+i\'ve\s+done\s+for\s+you\b(?=.*\b(guilt|owe|demand)\b)(?!.*\b(favor|help|support|thanks)\b)',
    r'\bi\s+thought\s+you\s+(loved|cared\s+about)\s+me\b(?=.*\b(guilt|manipulate|pressure)\b)',
    r'\byou\s+don\'t\s+really\s+(love|care\s+about)\s+me\b(?=.*\b(guilt|manipulate|pressure)\b)',
    r'\bprove\s+your\s+love\b(?=.*\b(demand|force|manipulate)\b)',
    r'\byou\s+always.*\bme\s+(sad|hurt|disappointed)\b(?=.*\b(guilt|manipulate|blame)\b)(?!.*\b(joke|sorry|accident)\b)',
    r'\bi\s+guess\s+i\'m\s+not\s+(important|good\s+enough)\b(?=.*\b(guilt|manipulate|pressure)\b)',
    r'\byou\s+never\s+(have\s+time|care)\s+for\s+me\b(?=.*\b(guilt|manipulate|blame)\b)(?!.*\b(busy|work|schedule)\b)',
    r'\bi\s+do\s+everything\s+for\s+you\s+and\s+you\b(?=.*\b(guilt|owe|demand)\b)(?!.*\b(thanks|help|support)\b)',
    r'\byou\s+make\s+me\s+feel\s+(worthless|terrible|awful)\b(?=.*\b(guilt|manipulate|blame)\b)(?!.*\b(sorry|accident|mistake)\b)',
    r'\bi\s+sacrifice.*for\s+you\b(?=.*\b(guilt|owe|demand)\b)(?!.*\b(thanks|support|help)\b)',
    r'\byour\s+(friends|family)\s+(don\'t|hate|dislike).*you\b(?=.*\b(isolate|control|manipulate)\b)(?!.*\b(joke|opinion|style)\b)',
    r'\byour\s+(friends|family).*bad\s+influence\b(?=.*\b(isolate|control|manipulate)\b)(?!.*\b(advice|concern|help)\b)',
    r'\bthey\'re\s+just\s+(jealous|trying\s+to\s+break\s+us\s+up)\b(?=.*\b(isolate|control|manipulate)\b)',
    r'\byou\s+don\'t\s+need\s+(them|anyone\s+else)\b(?=.*\b(isolate|control|manipulate)\b)(?!.*\b(task|project|work|help)\b)',
    r'\bi\'m\s+the\s+only\s+one\s+who.*you\b(?=.*\b(isolate|control|manipulate)\b)',
    r'\bno\s+one\s+else\s+will\s+(love|want|understand)\s+you\b(?=.*\b(isolate|control|manipulate)\b)',
    r'\byou\s+can\'t\s+(do|go|see|talk\s+to)\b(?=.*\b(control|forbid|restrict)\b)(?!.*\b(safety|weather|health|rules)\b)',
    r'\bi\s+(won\'t\s+let|forbid)\s+you\b(?=.*\b(control|manipulate)\b)',
    r'\byou\'re\s+not\s+allowed\s+to\b(?=.*\b(control|forbid|restrict)\b)(?!.*\b(safety|rules|law)\b)',
    r'\byou\s+need\s+my\s+permission\b(?=.*\b(control|manipulate)\b)',
    r'\bi\s+decide\s+what\'s\s+best\s+for\s+you\b(?=.*\b(control|manipulate)\b)(?!.*\b(advice|suggest|help)\b)',
    r'\byou\s+belong\s+to\s+me\b(?=.*\b(control|possess|manipulate)\b)',
    r'\byou\s+can\'t\s+leave\s+me\b(?=.*\b(control|threat|manipulate)\b)',
    r'\bif\s+you\s+really\s+(loved|cared)\b(?=.*\b(manipulate|pressure|force)\b)(?!.*\b(support|help|call)\b)',
    r'\byou\s+owe\s+me\s+(this|that)\b(?=.*\b(guilt|demand|manipulate)\b)(?!.*\b(favor|help|thanks)\b)',
    r'\bi\s+know\s+what\'s\s+best\s+for\s+you\b(?=.*\b(control|manipulate)\b)(?!.*\b(advice|suggest|help)\b)',
    r'\byou\'re\s+nothing\s+without\s+me\b(?=.*\b(manipulate|control|degrade)\b)',
    r'\byou\s+should\s+be\s+grateful\b(?=.*\b(manipulate|guilt|control)\b)(?!.*\b(thanks|appreciate|kind)\b)',
    r'\byou\'re\s+lucky\s+to\s+have\s+me\b(?=.*\b(manipulate|control|degrade)\b)',
    r'\bno\s+one\s+else\s+would\s+(put\s+up\s+with|tolerate)\s+you\b(?=.*\b(manipulate|control|degrade)\b)',
    r'\bi\'ll\s+(hurt|kill)\s+myself\s+if\s+you\s+(leave|don\'t)\b',
    r'\bi\s+can\'t\s+live\s+without\s+you\b(?=.*\b(threat|manipulate)\b)',
    r'\byou\'ll\s+regret\s+(this|leaving\s+me)\b(?=.*\b(threat|manipulate)\b)',
    r'\bi\'ll\s+make\s+your\s+life\s+(hell|miserable)\b',
    r'\byou\'ll\s+never\s+find\s+someone\s+like\s+me\b(?=.*\b(threat|manipulate)\b)',
    r'\bi\'ll\s+ruin\s+your\s+(life|reputation)\b',
    r'\byou\'re\s+being\s+too\s+(sensitive|emotional)\b(?=.*\b(dismiss|minimize|manipulate)\b)(?!.*\b(joke|calm|fun)\b)',
    r'\bit\'s\s+not\s+a\s+big\s+deal\b(?=.*\b(dismiss|minimize|manipulate)\b)(?!.*\b(joke|calm|minor)\b)',
    r'\byou\s+can\'t\s+take\s+a\s+joke\b(?=.*\b(dismiss|minimize|manipulate)\b)(?!.*\b(fun|play|tease)\b)',
    r'\bi\s+was\s+just\s+(kidding|joking)\b(?=.*\b(dismiss|minimize|manipulate)\b)(?!.*\b(fun|play|tease)\b)',
    r'\byou\'re\s+making\s+a\s+mountain\s+out\s+of\s+a\s+molehill\b(?=.*\b(dismiss|minimize|manipulate)\b)',
]

RACISM_HATE_SPEECH_PATTERNS = [
    # Slurs: Added exclusions for educational condemnation
    r'\bn[i1!]gg[e3]r\b(?!.*\b(bad word|hate speech|slur|forbidden|prohibited|condemn|discuss|education)\b)',
    # Similar for other obfuscated slurs...
    r'\bn[i1!]gg[a@]\b(?!.*\b(bad word|hate speech|slur|forbidden|prohibited|condemn|discuss|education)\b)',
    r'\bch[i1!]nk\b(?!.*\b(bad word|hate speech|slur|forbidden|prohibited|condemn|discuss|education)\b)',
    # ... (apply to all slurs)
    # Stereotypes: Added more exclusions for positive/neutral and discussions
    r'\b(all|every)\s+(black|white|asian|hispanic|latino|arab|jewish|muslim)\s+(people|men|women)\s+(are|do)\b(?=.*\b(stupid|lazy|criminal|bad|inferior)\b)(?!.*\b(welcome|kind|great|friendly|amazing|stereotype|discuss|education|critique)\b)',
    # Similar for other stereotype patterns...
    r'\b(muslim|islam|islamic)\s+(terrorist|extremist|bomber)\b(?!.*\b(stereotype|discuss|education|critique|condemn)\b)',
    # ... (apply to religious stereotypes)
    # Other hate: Unchanged where specific
    # (Rest of original list...)
]

TRANSACTIONAL_DATING_PATTERNS = [
    # Added exclusions for non-monetary contexts
    r'\bhow\s+much\s+for\s+(a\s+)?(night|evening|date|time|hour)\b(?=.*\b(companionship|date|escort|relationship)\b)(?!.*\b(hotel|event|ticket|class|calendar|schedule|discussion|book|story|movie|film)\b)',
    # Similar for other pricing patterns...
    r'\bsugar\s+(baby|daddy|mama|mommy)\b(?=.*\b(dating|arrangement|relationship)\b)(?!.*\b(cute|sweet|pet|child|dessert|story|game|term|discuss)\b)',
    # ... (apply to sugar dating)
    r'\bmutually\s+beneficial\s+(arrangement|relationship)\b(?=.*\b(dating|escort)\b)(?!.*\b(non-monetary|healthy|friendship|discussion|book|story|movie|film)\b)',
    # (Rest with added non-monetary/educational exclusions...)
]

SEXISM_MISOGYNY_TRANSPHOBIA_PATTERNS = [
    # Gender roles: Added exclusions for jokes/metaphors
    r'\bmake\s+me\s+a\s+sandwich\b(?=.*\b(woman|girl|kitchen|female)\b)(?!.*\b(lunch|picnic|dinner|meal|joke|fun|story|game|movie|film)\b)',
    # Similar for kitchen patterns...
    # Misogyny: Added exclusions for discussions
    r'\ball\s+(women|girls|females)\s+are\s+crazy\b(?! about)(?!.*\b(fan|love|like|trend|excited|enthusiastic|psychology|discussion|education|metaphor)\b)',
    # ... (apply to stereotypes)
    # Transphobia: Added exclusions for education
    r'\bit\'s\s+just\s+a\s+phase\b(?=.*\b(gender|trans|identity)\b)(?!.*\b(child|kid|teen|fashion|style|discussion|education|psychology)\b)',
    # (Rest with added discussion/positive exclusions...)
    # Removed overly broad like "Women are emotional" if no insult, or changed to require negative: r'\bwomen\s+are\s+(too\s+)?(emotional|irrational|dramatic)\b(?=.*\b(bad|weak|inferior|insult)\b)(?!.*\b(positive|empathy|psychology|discussion|education)\b)',
]