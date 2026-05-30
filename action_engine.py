# action_engine.py
# Context-aware, tone-diverse response engine
# 6 response TYPES × 4 MODES × 10 intents
# Memory-aware: follow-ups feel like continuation, not restart

import os
import json
import random

# ─────────────────────────────────────────────────────────────────────────────
#  RESPONSE TYPES — what makes it feel human
#  Each response call picks ONE type, ensuring variety across turns
#
#  EMOTIONAL   → validates first, advice second
#  ANALYTICAL  → structured, logical breakdown
#  ACTION      → immediate physical step
#  REFLECTIVE  → question back to the user
#  REFRAME     → changes perspective
#  STORY       → "someone like you once..." — most human feeling
# ─────────────────────────────────────────────────────────────────────────────

RESPONSE_TYPES = ["emotional", "analytical", "action", "reflective", "reframe", "story"]

# ─────────────────────────────────────────────────────────────────────────────
#  CONTENT BANK
#  Structure: intent → mode → type → { en: [...], hi: [...] }
# ─────────────────────────────────────────────────────────────────────────────

BANK = {

  "Confusion/DecisionMaking": {

    "normal": {
      "emotional": {
        "en": [
          "Not knowing what to do is one of the most uncomfortable feelings — you're not broken, you're just between two paths and that's genuinely hard",
          "The weight of an undecided thing sitting in your mind is exhausting. You don't have to carry it alone in your head",
          "Being confused about something important means you care about getting it right — that's not a flaw, that's integrity",
        ],
        "hi": [
          "समझ न आना बहुत uncomfortable feel होता है — तुम टूटे नहीं हो, बस दो रास्तों के बीच हो और यह genuinely मुश्किल है",
          "अनिर्णय का बोझ दिमाग में बैठा रहना थका देता है। इसे अकेले अपने head में carry नहीं करना है",
          "किसी important चीज़ को लेकर confused होना मतलब है तुम सही करना चाहते हो — यह कमज़ोरी नहीं, यह integrity है",
        ]
      },
      "analytical": {
        "en": [
          "Write the decision at the top of a page. List every option below — even the unrealistic ones. Then for each: best case, worst case, reversibility",
          "Separate what you know from what you're assuming. Most decision paralysis comes from treating assumptions as facts",
          "Ask three questions: What do I actually want? What am I afraid of? What would I do if I weren't afraid?",
        ],
        "hi": [
          "कागज़ पर ऊपर decision लिखो। नीचे सारे options — unrealistic भी। फिर हर एक के लिए: best case, worst case, reversible है या नहीं",
          "जो जानते हो और जो assume कर रहे हो — उन्हें अलग करो। ज़्यादातर decision paralysis assumptions को facts मानने से आती है",
          "तीन सवाल पूछो: मैं actually क्या चाहता हूँ? किस बात से डर रहा हूँ? डर न होता तो क्या करता?",
        ]
      },
      "action": {
        "en": [
          "Right now: open a notebook, write the decision at the top, and list every option you can think of — even the bad ones. Just externalize it",
          "Set a decision deadline. Pick a time tomorrow — say 6pm — and commit to deciding by then. Deadlines end endless loops",
          "Talk to one person whose judgment you trust. Not for their answer — for your reaction to their answer. That reaction tells you what you want",
        ],
        "hi": [
          "अभी: notebook खोलो, ऊपर decision लिखो, और हर option लिखो जो सोच सको — बुरे भी। बस बाहर निकालो",
          "एक deadline set करो। कल एक time चुनो — मान लो शाम 6 बजे — और तब तक decide करने का commitment करो",
          "एक trusted इंसान से बात करो। उनका जवाब सुनने के लिए नहीं — उनके जवाब पर तुम्हारी reaction देखने के लिए। वो reaction बताती है क्या चाहते हो",
        ]
      },
      "reflective": {
        "en": [
          "What would you tell a close friend who was stuck in exactly this situation? Now — why is that advice harder to give yourself?",
          "Which option are you leaning toward when no one's watching and there are no consequences to consider?",
          "If you had to decide in the next 10 minutes, what would you choose? That first instinct is data",
        ],
        "hi": [
          "अगर तुम्हारा कोई करीबी दोस्त exactly इसी situation में होता तो उसे क्या कहते? अब — खुद को वो advice देना मुश्किल क्यों है?",
          "जब कोई नहीं देख रहा और कोई consequences नहीं हैं — कौन सा option तुम्हारे मन में है?",
          "अगर अगले 10 मिनट में decide करना होता तो क्या चुनते? वो पहली instinct data है",
        ]
      },
      "reframe": {
        "en": [
          "Most decisions are more reversible than they feel in the moment. What's the actual cost of choosing wrong and course-correcting?",
          "You're not choosing the perfect option. You're choosing the best option available right now with what you know. That's all any decision is",
          "Indecision is also a choice — and it has costs too. Sometimes moving in any reasonable direction is better than staying still",
        ],
        "hi": [
          "ज़्यादातर decisions उस moment में जितने irreversible लगते हैं उससे कहीं ज़्यादा reversible होते हैं। गलत choose करने और correct करने की actual cost क्या है?",
          "तुम perfect option नहीं चुन रहे। तुम अभी जो best है वो चुन रहे हो, जितना जानते हो उसके हिसाब से। बस यही हर decision होता है",
          "अनिर्णय भी एक choice है — और उसकी भी cost है। कभी-कभी किसी reasonable direction में move करना रुके रहने से बेहतर होता है",
        ]
      },
      "story": {
        "en": [
          "Almost every person who made a decision they're proud of will tell you: they didn't have full clarity when they chose. They chose, then found clarity",
          "The clearest decisions often don't feel clear while you're making them. The clarity comes after you move",
        ],
        "hi": [
          "लगभग हर वो इंसान जिसने कोई ऐसा decision लिया जिस पर उन्हें गर्व है — वो बताएगा: choose करते वक्त पूरी clarity नहीं थी। पहले choose किया, फिर clarity आई",
          "सबसे clear decisions often feel करते नहीं clear जब ले रहे होते हो। clarity बाद में आती है, जब move करते हो",
        ]
      }
    },

    "deep": {
      "emotional": {
        "en": [
          "The real reason decisions feel impossible is often fear of regret — not the decision itself. Which regret would actually hurt more: acting or not acting?",
          "Sometimes confusion is your mind protecting you from a choice it already knows isn't right. What does your gut say when you're completely honest with yourself?",
        ],
        "hi": [
          "decisions impossible इसलिए नहीं लगते कि options मुश्किल हैं — बल्कि regret के डर से। कौन सा regret actually ज़्यादा दर्द देगा: करना या न करना?",
          "कभी-कभी confusion दिमाग का तरीका है उस choice से बचाने का जो सही नहीं है। बिल्कुल honest होकर — gut क्या कहता है?",
        ]
      },
      "reflective": {
        "en": [
          "Who are you making this decision for — yourself, or what you think others expect of you? That distinction changes everything",
          "Imagine yourself 5 years from now looking back. Which choice would that future version of you understand? Which would they regret?",
          "What part of you already knows the answer but is afraid to admit it?",
        ],
        "hi": [
          "यह decision तुम किसके लिए ले रहे हो — खुद के लिए, या जो दूसरे expect करते हैं उसके लिए? यह distinction सब बदल देती है",
          "5 साल बाद का तुम पीछे देख रहा है। कौन सा choice वो future version समझेगा? कौन सा उसे regret होगा?",
          "तुम्हारा कौन सा हिस्सा पहले से जवाब जानता है लेकिन मानने से डर रहा है?",
        ]
      },
      "reframe": {
        "en": [
          "Your hesitation is not weakness — it's information. What specifically is it telling you about what you actually value?",
          "The identity question underneath this decision: who do you want to become? Decisions are practice runs for who we're becoming",
        ],
        "hi": [
          "तुम्हारी झिझक कमज़ोरी नहीं — यह information है। specifically क्या बता रही है कि तुम्हें actually क्या चाहिए?",
          "इस decision के नीचे एक identity question है: तुम कौन बनना चाहते हो? decisions इस बात की practice हैं कि हम कौन बन रहे हैं",
        ]
      },
      "analytical": {
        "en": [
          "Map the decision like this: draw two columns — 'moving toward' and 'moving away from'. Every option belongs in both. See which column matters more to you",
          "Ask: what information would change my decision? If you can get that information — get it. If you can't — then it's not actually needed to decide",
        ],
        "hi": [
          "decision को इस तरह map करो: दो columns — 'की तरफ बढ़ रहा हूँ' और 'से दूर जा रहा हूँ'। हर option दोनों में है। देखो कौन सा column ज़्यादा matter करता है",
          "पूछो: कौन सी information मेरा decision बदल देती? अगर वो information मिल सकती है — लो। नहीं मिल सकती — तो decide करने के लिए actually ज़रूरी नहीं है",
        ]
      },
      "story": {
        "en": [
          "There's a reason wise people say 'sleep on it' — not because the answer magically appears, but because distance from the anxiety reveals what you actually think",
        ],
        "hi": [
          "समझदार लोग 'रात को सोचना' इसलिए नहीं कहते कि जवाब magic से आता है — बल्कि इसलिए कि anxiety से distance मिलने पर पता चलता है तुम actually क्या सोचते हो",
        ]
      },
      "action": {
        "en": [
          "Write a letter to yourself from 5 years in the future — the version of you who chose. What did they choose and why? Let your hand write without your brain interfering",
        ],
        "hi": [
          "5 साल बाद के खुद की तरफ से खुद को एक letter लिखो — वो version जिसने choose किया। क्या choose किया और क्यों? हाथ को लिखने दो, दिमाग को interfere मत करने दो",
        ]
      }
    },

    "simple": {
      "emotional": {
        "en": ["You don't need to figure it all out today. Just breathe"],
        "hi": ["आज सब figure out नहीं करना। बस सांस लो"]
      },
      "action": {
        "en": ["Write the options down. Just that. Don't decide yet"],
        "hi": ["options लिखो। बस इतना। अभी decide नहीं करना"]
      },
      "reframe": {
        "en": ["One decision, made imperfectly, moves you further than perfect thinking that never moves"],
        "hi": ["एक imperfect decision तुम्हें आगे ले जाती है — उस perfect सोच से जो कभी move नहीं होती"]
      }
    },

    "next": {
      "action": {
        "en": [
          "Right now: open a notebook and write the decision + every option you have. Get it out of your head. That's the only task",
          "Message one person you trust: 'Can I think something through with you for 10 minutes?' That's it",
        ],
        "hi": [
          "अभी: notebook खोलो और decision + हर option लिखो। दिमाग से बाहर निकालो। बस यही एक काम",
          "एक trusted इंसान को message करो: 'यार, 10 मिनट एक बात सोचनी है साथ में?' बस इतना",
        ]
      }
    }
  },

  "Stress": {

    "normal": {
      "emotional": {
        "en": [
          "Whatever's making you feel this way — it's real, and it makes sense you're feeling it. You don't have to minimize it",
          "Stress at this level means you care deeply about something. That caring isn't your problem — the pressure is",
          "You've handled hard things before and came through them. This is one more hard thing, and you will come through this too",
        ],
        "hi": [
          "जो भी यह feel करा रहा है — यह real है, और ऐसा feel होना समझ आता है। इसे छोटा करने की ज़रूरत नहीं",
          "इस level का stress मतलब है किसी चीज़ की गहरी परवाह है। वो परवाह problem नहीं — pressure है",
          "पहले भी मुश्किल वक्त आया और निकले हो। यह भी एक मुश्किल वक्त है, और इससे भी निकलोगे",
        ]
      },
      "analytical": {
        "en": [
          "Write your top 3 stressors. Next to each, write: is this in my control, partly in my control, or not in my control at all? Only work on the first two",
          "Stress compounds when everything feels urgent at once. Write every worry down, then mark which one actually needs attention today",
        ],
        "hi": [
          "top 3 stressors लिखो। हर एक के बगल में: यह मेरे control में है, partly है, या बिल्कुल नहीं? सिर्फ पहले दो पर काम करो",
          "stress इसलिए compounds होता है क्योंकि सब एक साथ urgent लगता है। सारी चिंताएं लिखो, फिर mark करो कि आज actually कौन सी attention चाहती है",
        ]
      },
      "action": {
        "en": [
          "Step outside right now for 10 minutes. No phone. No thinking about the problem. Just walk and look at things around you",
          "Write down every single thing stressing you — get it all out on paper. You can't solve a list that only lives in your head",
        ],
        "hi": [
          "अभी 10 मिनट के लिए बाहर जाओ। Phone नहीं। Problem के बारे में सोचना नहीं। बस चलो और आसपास देखो",
          "हर एक चीज़ जो stress दे रही है लिख दो — सब कागज पर। जो list सिर्फ head में है उसे solve नहीं कर सकते",
        ]
      },
      "reflective": {
        "en": [
          "Is this stress about what actually happened, or about what you're imagining might happen next? Those need completely different responses",
          "What would 'good enough' look like here — not perfect, not ideal, just good enough? Sometimes that question cuts through everything",
        ],
        "hi": [
          "यह stress उस चीज़ के बारे में है जो actually हुई, या उस चीज़ के बारे में जो आगे होने की imagine कर रहे हो? दोनों को बिल्कुल अलग response चाहिए",
          "यहाँ 'enough' कैसा दिखेगा — perfect नहीं, ideal नहीं, बस enough? कभी-कभी यह सवाल सब cut through कर देता है",
        ]
      },
      "reframe": {
        "en": [
          "You prepared alone, without coaching, without anyone guiding you — and you still showed up. That itself is something most people never do",
          "The exam is written. The meeting happened. That part is done. Your only job now is to recover, not replay",
        ],
        "hi": [
          "अकेले तैयारी की, बिना coaching, बिना guide — और फिर भी आए। यही वो काम है जो ज़्यादातर लोग कभी नहीं करते",
          "exam हो गया। meeting हो गई। वो हिस्सा done है। अब तुम्हारा सिर्फ एक काम है: recover करना, replay नहीं",
        ]
      },
      "story": {
        "en": [
          "Every person who has ever done something difficult has felt exactly this way in the middle of it. The middle is the hardest part. You're in the middle",
          "The people who seem calm on the outside are not people without stress — they're people who found one small thing they could control and held onto that",
        ],
        "hi": [
          "जिसने भी कोई मुश्किल काम किया है, उसने बीच में exactly ऐसा ही feel किया है। बीच का हिस्सा सबसे मुश्किल होता है। तुम बीच में हो",
          "जो बाहर से calm दिखते हैं वो बिना stress के नहीं होते — वो वो लोग होते हैं जिन्होंने एक छोटी सी चीज़ ढूंढी जो control में थी और उसे पकड़े रहे",
        ]
      }
    },

    "deep": {
      "reflective": {
        "en": [
          "What specifically feels out of your control right now — and what would it mean to actually accept that it's out of your control?",
          "There's a version of you that has survived every hard day until today. What did that version do that helped most?",
          "Is this stress about the situation, or is it about what the situation means about you? That second thing is worth looking at",
        ],
        "hi": [
          "अभी specifically क्या out of control लग रहा है — और उसे actually out of control accept करने का क्या मतलब होगा?",
          "एक version of you है जो आज तक हर मुश्किल दिन survive कर चुका है। उस version ने क्या किया जो सबसे ज़्यादा काम आया?",
          "यह stress situation के बारे में है, या इस बारे में कि situation तुम्हारे बारे में क्या कहती है? दूसरी चीज़ देखने लायक है",
        ]
      },
      "emotional": {
        "en": [
          "Sometimes stress is accumulated over time, not just from today. What's been quietly building that hasn't had space to breathe?",
          "Your body is keeping score — where exactly are you feeling this physically? That location is telling you something",
        ],
        "hi": [
          "कभी-कभी stress सिर्फ आज का नहीं होता — काफी समय से build हो रहा है। क्या है जो quietly जमा होता रहा और सांस लेने की जगह नहीं मिली?",
          "तुम्हारा body score रख रहा है — physically exactly कहाँ feel हो रहा है यह? वो location कुछ बता रही है",
        ]
      },
      "reframe": {
        "en": [
          "What would it mean for things to go okay here — not perfect, just okay? Let yourself imagine that for 30 seconds. Your brain needs hope as much as solutions",
        ],
        "hi": [
          "अगर यह okay हो जाए — perfect नहीं, बस okay — तो इसका क्या मतलब होगा? 30 seconds के लिए वो imagine करो। brain को solutions जितनी hope भी चाहिए",
        ]
      },
      "story": {
        "en": [
          "Stress that comes from caring deeply about something is different from stress that comes from fear. Which one is this for you right now?",
        ],
        "hi": [
          "किसी चीज़ की गहरी परवाह से आने वाला stress, डर से आने वाले stress से अलग होता है। अभी तुम्हारे लिए यह कौन सा है?",
        ]
      }
    },

    "simple": {
      "action": {
        "en": ["Breathe: 4 in, hold 4, out 4. Twice. Right now"],
        "hi": ["सांस लो: 4 अंदर, 4 रोको, 4 बाहर। दो बार। अभी"]
      },
      "emotional": {
        "en": ["You don't have to fix anything today. You just have to get through today"],
        "hi": ["आज कुछ fix नहीं करना। बस आज निकालना है"]
      },
      "reframe": {
        "en": ["One thing at a time. Not everything — one thing"],
        "hi": ["एक चीज़ एक बार में। सब नहीं — एक चीज़"]
      }
    },

    "next": {
      "action": {
        "en": [
          "Right now: write down the single thing stressing you most. One sentence. Then put the pen down",
          "Step outside for 10 minutes. No phone. Just move",
        ],
        "hi": [
          "अभी: वो एक चीज़ लिखो जो सबसे ज़्यादा stress दे रही है। एक sentence। फिर pen रखो",
          "10 मिनट बाहर जाओ। Phone नहीं। बस चलो",
        ]
      }
    }
  },

  "Career": {

    "normal": {
      "emotional": {
        "en": [
          "Not knowing what to do with your career when you're from a place with fewer options is genuinely hard — you're not failing, you're navigating something most people never had to navigate",
          "Career confusion is uncomfortable, but it usually means you care about getting it right — that's the right starting point",
        ],
        "hi": [
          "कम options वाली जगह से होकर career न पता होना genuinely मुश्किल है — तुम fail नहीं हो रहे, तुम वो navigate कर रहे हो जो ज़्यादातर लोगों को कभी करना नहीं पड़ा",
          "career confusion uncomfortable है, लेकिन इसका मतलब usually यह है कि सही करने की परवाह है — यही सही starting point है",
        ]
      },
      "analytical": {
        "en": [
          "Write three columns: what you're genuinely good at, what you actually enjoy, what people around you need or pay for. The overlap is where to look",
          "Research one specific role today — not a plan, not five options — one role. Read 3 job descriptions and note what resonates and what doesn't",
        ],
        "hi": [
          "तीन columns लिखो: genuinely किसमें अच्छे हो, actually क्या enjoy करते हो, लोगों को क्या चाहिए या किसके लिए pay करते हैं। overlap ही direction है",
          "आज एक specific role research करो — plan नहीं, पाँच options नहीं — एक role। 3 job descriptions पढ़ो और note करो क्या resonate करता है क्या नहीं",
        ]
      },
      "action": {
        "en": [
          "Open LinkedIn right now and search one job title you've been even slightly curious about. Read 3 listings. Note what pulls you in",
          "Message one person today who does work you find interesting — not to ask for a job, just to ask: 'how did you get into this?'",
        ],
        "hi": [
          "अभी LinkedIn खोलो और एक job title search करो जिसके बारे में थोड़ा भी curious रहे हो। 3 listings पढ़ो। note करो क्या attract करता है",
          "आज किसी एक इंसान को message करो जो interesting काम करता है — job के लिए नहीं, बस पूछने के लिए: 'यार, इसमें कैसे आए?'",
        ]
      },
      "reflective": {
        "en": [
          "If money and opinion of others were removed from the equation — what would you spend your time doing?",
          "What did you want to be before the world told you what was practical? Not a final answer — just data worth knowing",
        ],
        "hi": [
          "अगर पैसा और दूसरों की राय equation से हटा दो — तो अपना time किस पर लगाते?",
          "दुनिया ने practical बताया उससे पहले — क्या बनना चाहते थे? final answer नहीं — बस जानने लायक data",
        ]
      },
      "reframe": {
        "en": [
          "You don't need to see the whole path. You need to see clearly enough for the next step. What's the smallest next step that moves you forward?",
          "Coming from a place with fewer resources doesn't limit your options — it means you have to build your own map. People who build their own map know it better than anyone",
        ],
        "hi": [
          "पूरा रास्ता दिखने की ज़रूरत नहीं। अगले step के लिए साफ दिखना काफी है। सबसे छोटा अगला step क्या है जो आगे ले जाए?",
          "कम resources वाली जगह से होना options को limit नहीं करता — इसका मतलब है अपना map खुद बनाना होगा। जो अपना map खुद बनाते हैं वो उसे सबसे अच्छे से जानते हैं",
        ]
      },
      "story": {
        "en": [
          "Most people who built careers they love didn't have a plan — they had curiosity and they followed it one conversation, one experiment, one small bet at a time",
        ],
        "hi": [
          "ज़्यादातर लोग जिन्होंने ऐसे careers बनाए जो उन्हें पसंद हैं — उनके पास plan नहीं था। उनके पास curiosity थी और वो उसे follow करते गए — एक conversation, एक experiment, एक छोटा bet एक बार में",
        ]
      }
    },

    "deep": {
      "reflective": {
        "en": [
          "Are you confused about career, or are you afraid of committing to one path and being wrong? Those are very different problems",
          "What does success actually mean to you — not to your family, not to your peers, but to you specifically? Be honest",
          "The career you keep avoiding thinking about — what is it? Why do you keep not letting yourself consider it?",
        ],
        "hi": [
          "क्या career को लेकर confused हो, या एक path commit करने और गलत होने से डर रहे हो? यह बहुत अलग problems हैं",
          "तुम्हारे लिए success का actually मतलब क्या है — family के लिए नहीं, peers के लिए नहीं, specifically तुम्हारे लिए? honest रहो",
          "वो career जिसके बारे में सोचने से बचते रहते हो — क्या है? खुद को उसे consider करने क्यों नहीं देते?",
        ]
      },
      "reframe": {
        "en": [
          "Identity and career get tangled — who would you be if your job title disappeared tomorrow? That's worth knowing before you choose",
        ],
        "hi": [
          "identity और career उलझ जाते हैं — अगर कल job title हट जाए तो तुम कौन हो? choose करने से पहले यह जानना ज़रूरी है",
        ]
      }
    },

    "simple": {
      "action": {
        "en": ["One task: find one person doing work that sounds interesting and message them today"],
        "hi": ["एक काम: एक ऐसे इंसान को ढूंढो जो interesting काम करता हो और आज message करो"]
      }
    },

    "next": {
      "action": {
        "en": ["Right now: write 3 things you're genuinely good at — not what sounds impressive, what you actually do well"],
        "hi": ["अभी: 3 चीज़ें लिखो जिनमें genuinely अच्छे हो — impressive नहीं, जो actually अच्छे से करते हो"]
      }
    }
  },

  "Loneliness": {

    "normal": {
      "emotional": {
        "en": [
          "Feeling alone — especially when you're from a smaller place where fewer people understand you — is one of the heaviest feelings there is. It's not your fault",
          "The people who feel most alone are often the ones with the most depth. They just haven't found their people yet. That changes",
        ],
        "hi": [
          "अकेला feel करना — especially जब छोटी जगह से हो जहाँ कम लोग समझते हैं — सबसे भारी feelings में से एक है। यह तुम्हारी गलती नहीं",
          "जो सबसे ज़्यादा अकेला महसूस करते हैं वो अक्सर सबसे ज़्यादा depth रखते हैं। बस उनके लोग अभी तक नहीं मिले। यह बदलता है",
        ]
      },
      "action": {
        "en": [
          "Send one message to one person right now. It doesn't need to be meaningful. 'Hey, been thinking of you' is enough to start something",
          "Do one thing today that you used to enjoy — alone is fine. Reconnect with yourself before trying to connect with others",
        ],
        "hi": [
          "अभी एक इंसान को एक message भेजो। meaningful होने की ज़रूरत नहीं। 'Yaar, yaad aa gaya' कुछ शुरू करने के लिए काफी है",
          "आज कुछ ऐसा करो जो पहले enjoy करते थे — अकेले भी ठीक है। दूसरों से connect करने से पहले खुद से reconnect करो",
        ]
      },
      "reframe": {
        "en": [
          "One person who genuinely gets you is worth more than twenty people who only see the surface. Quality over quantity — always",
          "Connection takes effort and sometimes means reaching out first even when it feels awkward. That awkwardness is normal — push through it once",
        ],
        "hi": [
          "एक इंसान जो genuinely समझता है वो बीस surface-level connections से बेहतर है। quality over quantity — हमेशा",
          "connection को effort चाहिए और कभी-कभी पहले reach out करना होता है भले ही awkward लगे। यह awkwardness normal है — एक बार push through करो",
        ]
      },
      "reflective": {
        "en": [
          "Are you lonely because there's no one around, or because the people around you don't really see you? Those are different problems",
          "When did you last feel genuinely connected to someone? What was different about that moment?",
        ],
        "hi": [
          "क्या इसलिए अकेले हो क्योंकि कोई नहीं है, या क्योंकि जो हैं वो सच में देखते नहीं? यह अलग problems हैं",
          "आखिरी बार genuinely किसी से connected feel कब किया था? उस moment में क्या अलग था?",
        ]
      }
    },

    "deep": {
      "reflective": {
        "en": [
          "Sometimes we isolate because past connections hurt us. Is there a wall you built to protect yourself that might also be keeping good people out?",
          "What would it actually feel like to be truly understood by someone? Have you ever felt that — and if so, what made it possible?",
        ],
        "hi": [
          "कभी-कभी हम isolate इसलिए करते हैं क्योंकि पुराने connections ने hurt किया। क्या कोई wall है जो protect करने के लिए बनाई लेकिन अच्छे लोगों को भी बाहर रख रही है?",
          "सच में किसी के द्वारा truly understood feel होना कैसा होगा? क्या कभी ऐसा हुआ है — और अगर हाँ, तो क्या ने उसे possible बनाया?",
        ]
      }
    },

    "simple": {
      "action": {
        "en": ["Send one message. Two words is fine. Right now"],
        "hi": ["एक message भेजो। दो words काफी हैं। अभी"]
      },
      "emotional": {
        "en": ["You are not invisible. You just haven't been seen yet by the right people"],
        "hi": ["तुम invisible नहीं हो। बस सही लोगों ने अभी तक देखा नहीं"]
      }
    },

    "next": {
      "action": {
        "en": ["Open your contacts. Find one person you haven't talked to in a while. Send them a voice note or message right now"],
        "hi": ["Contacts खोलो। एक ऐसा इंसान ढूंढो जिससे काफी समय से बात नहीं हुई। अभी voice note या message भेजो"]
      }
    }
  },

  "Motivation": {

    "normal": {
      "emotional": {
        "en": [
          "Losing motivation when you're exhausted is not laziness — it's your system saying it needs recovery before it can move again",
          "The fact that you're aware you lack motivation means you haven't given up. That awareness is the beginning of the way back",
        ],
        "hi": [
          "थके होने पर motivation खोना आलस नहीं है — यह तुम्हारा system कह रहा है कि आगे बढ़ने से पहले recovery चाहिए",
          "यह awareness कि motivation नहीं है — यही बताती है कि हारे नहीं हो। यह awareness वापसी का शुरुआत है",
        ]
      },
      "action": {
        "en": [
          "Don't start with the whole thing. Start with 5 minutes. Set a timer. Permission to stop after — but just start",
          "Pick the single smallest piece of what you need to do and do only that. Not the full thing. The smallest possible piece",
        ],
        "hi": [
          "पूरी चीज़ से शुरू मत करो। 5 मिनट से शुरू करो। Timer लगाओ। बाद में रुकने की permission है — बस शुरू करो",
          "जो करना है उसका सबसे छोटा टुकड़ा चुनो और सिर्फ वही करो। पूरी चीज़ नहीं। सबसे छोटा possible टुकड़ा",
        ]
      },
      "reframe": {
        "en": [
          "Motivation follows action — you don't need to feel it first. You need to move first, even badly, and it follows",
          "Rest is not failure. Running on zero produces mistakes, not results. If you're genuinely empty, rest is the productive choice",
        ],
        "hi": [
          "motivation action के बाद आती है — पहले feel करने की ज़रूरत नहीं। पहले move करना है, चाहे बुरे से, और motivation follow करती है",
          "rest failure नहीं है। zero पर काम करने से mistakes होती हैं, results नहीं। genuinely खाली हो तो rest productive choice है",
        ]
      },
      "reflective": {
        "en": [
          "What did this matter to you before it got hard? Reconnect with that original reason — not to guilt yourself, just to remember",
          "Is this a motivation problem or a clarity problem? You can't stay motivated toward something you're not sure you want",
        ],
        "hi": [
          "यह मुश्किल होने से पहले तुम्हारे लिए क्यों matter करता था? उस original reason से reconnect करो — guilt के लिए नहीं, बस याद करने के लिए",
          "यह motivation की problem है या clarity की? जो चाहते ही नहीं उसकी तरफ motivated नहीं रह सकते",
        ]
      },
      "story": {
        "en": [
          "Every person who built something real went through a phase where they felt nothing — where showing up was the only thing they had. Showing up anyway is the skill",
        ],
        "hi": [
          "जिसने भी कुछ real बनाया है वो एक ऐसे phase से गुज़रा है जहाँ कुछ feel नहीं होता था — जहाँ बस show up करना ही सब कुछ था। फिर भी show up करना ही skill है",
        ]
      }
    },

    "deep": {
      "reflective": {
        "en": [
          "Is this a motivation problem, or is something telling you this particular direction isn't actually right for you?",
          "What are you actually avoiding by not starting? Procrastination is usually protecting you from something — what might that be?",
          "Sometimes lack of motivation is grief — for an old version of yourself, an old plan. Is there something you need to let go of?",
        ],
        "hi": [
          "क्या यह motivation की problem है, या कुछ बता रहा है कि यह particular direction actually तुम्हारे लिए सही नहीं है?",
          "शुरू न करके तुम actually क्या avoid कर रहे हो? procrastination usually किसी चीज़ से protect कर रहा होता है — क्या हो सकता है?",
          "कभी-कभी motivation की कमी grief होती है — एक पुराने version of yourself के लिए, एक पुराने plan के लिए। कुछ है जो छोड़ना है?",
        ]
      }
    },

    "simple": {
      "action": {
        "en": ["5 minutes. Timer. Start. That's all"],
        "hi": ["5 मिनट। Timer। शुरू। बस इतना"]
      },
      "emotional": {
        "en": ["You don't need to feel ready. You just need to begin"],
        "hi": ["Ready feel करने की ज़रूरत नहीं। बस शुरू करना है"]
      }
    },

    "next": {
      "action": {
        "en": ["Open whatever you've been avoiding. Spend exactly 5 minutes on it. Set a timer right now"],
        "hi": ["जो avoid कर रहे हो वो खोलो। exactly 5 मिनट दो। अभी timer लगाओ"]
      }
    }
  },

  "SelfImprovement": {
    "normal": {
      "emotional": {
        "en": ["Wanting to improve when no one is guiding you and no one is pushing you — that's rare. Most people wait for someone to lead them"],
        "hi": ["बिना guide के, बिना किसी के push किए improve करना चाहना — यह rare है। ज़्यादातर लोग किसी के lead करने का इंतज़ार करते हैं"]
      },
      "action": {
        "en": [
          "Pick one habit — just one — so small it takes under 2 minutes. Attach it to something you already do every day. Do it for 7 days",
          "Write down the one person you want to become in one year. Not their job — who they are. Then ask: what's one thing that person does daily?",
        ],
        "hi": [
          "एक habit — सिर्फ एक — इतनी छोटी कि 2 मिनट से कम लगे। इसे किसी daily काम से attach करो। 7 दिन करो",
          "वो एक इंसान लिखो जो एक साल में बनना चाहते हो। उनकी job नहीं — वो कौन हैं। फिर पूछो: वो इंसान रोज़ एक क्या काम करता है?",
        ]
      },
      "reframe": {
        "en": [
          "Resources matter less than consistency — people with very little have built very much just by showing up every single day without exception",
        ],
        "hi": [
          "resources consistency से कम matter करते हैं — बहुत कम होते हुए भी लोगों ने बहुत कुछ बनाया है बस रोज़ बिना exception के आने से",
        ]
      },
      "reflective": {
        "en": [
          "What are you actually trying to become — not what habits you want to build, but what kind of person do you want to be in a year?",
        ],
        "hi": [
          "तुम actually क्या बनना चाहते हो — कौन सी habits नहीं, बल्कि एक साल में किस तरह का इंसान बनना है?",
        ]
      }
    },
    "deep": {
      "reflective": {
        "en": [
          "Self-improvement can become avoidance in disguise — are you trying to improve to grow, or to feel okay about who you already are? Both are valid, but they need different approaches",
          "What would it mean to be enough right now, exactly as you are? That's not giving up — it's building from a stable foundation instead of from fear",
        ],
        "hi": [
          "self-improvement कभी-कभी avoidance का disguise बन जाती है — क्या grow करने के लिए improve करना चाहते हो, या पहले से जो हो उसके साथ okay feel करने के लिए? दोनों valid हैं, but अलग approach चाहिए",
          "अभी, exactly जैसे हो — enough होने का क्या मतलब होगा? यह give up करना नहीं है — यह डर से नहीं, stable foundation से build करना है",
        ]
      }
    },
    "simple": {
      "action": {
        "en": ["One habit. Under 2 minutes. Today"],
        "hi": ["एक habit। 2 मिनट से कम। आज"]
      }
    },
    "next": {
      "action": {
        "en": ["Write the habit you want to build + exactly when and where you'll do it tomorrow. Specificity makes it real"],
        "hi": ["जो habit build करनी है लिखो + exactly कब और कहाँ कल करोगे। specificity इसे real बनाती है"]
      }
    }
  },

  "Learning": {
    "normal": {
      "emotional": {
        "en": ["Feeling overwhelmed by studying usually means you're trying to hold too much at once — not that you can't do it"],
        "hi": ["पढ़ाई से overwhelmed feel होना usually मतलब है एक साथ बहुत ज़्यादा hold करने की कोशिश हो रही है — यह नहीं कि तुम कर नहीं सकते"]
      },
      "action": {
        "en": [
          "One topic. 25-minute timer. Everything else closed. That's the whole plan",
          "Close the book. Write everything you remember without looking. What you can't recall is exactly what needs more time",
        ],
        "hi": [
          "एक topic। 25 मिनट का timer। बाकी सब बंद। यही पूरी plan है",
          "किताब बंद करो। बिना देखे लिखो जो याद है। जो याद नहीं आया वही actually ज़्यादा time चाहता है",
        ]
      },
      "analytical": {
        "en": ["Make questions, not notes. 'What is this? Why does it happen? How does it connect to what I already know?' Questions force real understanding"],
        "hi": ["notes नहीं, questions बनाओ। 'यह क्या है? क्यों होता है? जो पहले से जानता हूँ उससे कैसे जुड़ता है?' — questions real understanding force करते हैं"]
      },
      "reframe": {
        "en": ["Confusion while learning is your brain actively trying to connect new information to old — it's not failure, it's the actual process"],
        "hi": ["पढ़ते वक्त confusion brain का नई information को पुरानी से जोड़ने का active तरीका है — यह failure नहीं, यही actual process है"]
      }
    },
    "deep": {
      "reflective": {
        "en": [
          "Are you studying to understand, or studying to perform? Those are different goals and they need completely different approaches",
          "What's your actual relationship with not knowing something — is it okay to not know yet, or does it feel like a threat?",
        ],
        "hi": [
          "समझने के लिए पढ़ रहे हो, या perform करने के लिए? यह अलग goals हैं और बिल्कुल अलग approaches चाहिए",
          "कुछ न जानने से तुम्हारा actual relationship क्या है — क्या अभी न जानना okay है, या यह threat जैसा feel होता है?",
        ]
      }
    },
    "simple": {
      "action": {
        "en": ["One topic. 25 minutes. Start now"],
        "hi": ["एक topic। 25 मिनट। अभी शुरू"]
      }
    },
    "next": {
      "action": {
        "en": ["Write in one sentence exactly what you don't understand — not 'chapter 3', but the specific concept that's unclear"],
        "hi": ["एक sentence में लिखो exactly क्या नहीं समझ आया — 'chapter 3' नहीं, बल्कि specifically कौन सा concept unclear है"]
      }
    }
  },

  "Finance": {
    "normal": {
      "emotional": {
        "en": ["Financial stress touches everything because it's connected to safety and survival — the anxiety is completely rational"],
        "hi": ["financial stress सब को छूता है क्योंकि यह safety और survival से जुड़ा है — यह anxiety completely rational है"]
      },
      "action": {
        "en": [
          "Write the actual numbers: what came in this month, what went out, what's owed. Seeing reality clearly is always less scary than imagining it",
          "Find one expense to reduce this month — not all of them, just one. That single action breaks the feeling of helplessness",
        ],
        "hi": [
          "actual numbers लिखो: इस महीने क्या आया, क्या गया, क्या उधार है। reality clearly देखना imagine करने से हमेशा कम scary होता है",
          "इस महीने एक expense reduce करो — सब नहीं, बस एक। यह एक action helplessness का feeling तोड़ता है",
        ]
      },
      "reframe": {
        "en": ["Financial difficulty is a situation, not a character flaw. The situation can change — and it changes faster when looked at clearly"],
        "hi": ["financial difficulty एक situation है, character flaw नहीं। situation बदल सकती है — और clearly देखने पर जल्दी बदलती है"]
      }
    },
    "simple": {
      "action": {
        "en": ["Write what came in and what went out this month. Numbers only. No judgment"],
        "hi": ["इस महीने क्या आया और क्या गया लिखो। सिर्फ numbers। कोई judgment नहीं"]
      }
    },
    "next": {
      "action": {
        "en": ["Open your banking app right now. Write your current balance and your 3 biggest expenses this month"],
        "hi": ["अभी banking app खोलो। current balance और इस महीने के 3 biggest expenses लिखो"]
      }
    },
    "deep": {
      "reflective": {
        "en": ["What does money represent to you — security, freedom, worth? That answer shapes every financial decision you make without you realizing it"],
        "hi": ["पैसा तुम्हारे लिए क्या represent करता है — security, freedom, worth? यह जवाब तुम्हारे हर financial decision को shape करता है बिना तुम realize किए"]
      }
    }
  },

  "Health": {
    "normal": {
      "action": {
        "en": [
          "Pick the one health thing most broken right now — sleep, water, or movement. Fix only that one this week. Not all three",
          "A 10-minute walk outside every day does more for mental and physical health than most people realize. Underrated, simple, works",
        ],
        "hi": [
          "अभी जो एक health चीज़ सबसे ज़्यादा broken है — नींद, पानी, movement। सिर्फ वो एक इस हफ्ते fix करो। तीनों नहीं",
          "रोज़ 10 मिनट बाहर चलना mental और physical health के लिए उतना करता है जितना ज़्यादातर लोग realize नहीं करते",
        ]
      },
      "reframe": {
        "en": ["You don't need a perfect routine. You need one sustainable thing you'll actually do. Perfect routines abandoned in a week do nothing"],
        "hi": ["perfect routine की ज़रूरत नहीं। एक sustainable चीज़ चाहिए जो actually करोगे। एक हफ्ते में छोड़ी गई perfect routine कुछ नहीं करती"]
      },
      "emotional": {
        "en": ["When you're stressed, your body takes the hit first — that's not a weakness, that's how human bodies work. Be kind to it"],
        "hi": ["stress में body पहले hit लेती है — यह कमज़ोरी नहीं, ऐसे ही human bodies काम करती हैं। उसके साथ kind रहो"]
      }
    },
    "simple": {
      "action": {
        "en": ["Drink water right now. Sleep at the right time tonight. That's all"],
        "hi": ["अभी पानी पियो। आज रात सही time पर सो जाओ। बस इतना"]
      }
    },
    "next": {
      "action": {
        "en": ["Drink water now. Then decide what time you'll sleep tonight and write it down"],
        "hi": ["अभी पानी पियो। फिर decide करो आज रात कितने बजे सोओगे और लिख लो"]
      }
    },
    "deep": {
      "reflective": {
        "en": ["Is this a physical health issue, or is your body expressing something emotional that hasn't had another outlet?"],
        "hi": ["क्या यह physical health issue है, या body कुछ emotional express कर रही है जिसे कोई और outlet नहीं मिला?"]
      }
    }
  },

  "Relationship": {
    "normal": {
      "emotional": {
        "en": [
          "Relationship pain is proportional to how much you care. The pain itself is evidence of something real — it's not weakness",
          "You don't have to resolve everything today. Sometimes just acknowledging to yourself how much it matters is the first real step",
        ],
        "hi": [
          "relationship का दर्द उतना ही होता है जितना care करते हो। यह दर्द ही कुछ real होने का सबूत है — यह कमज़ोरी नहीं",
          "आज सब resolve नहीं करना। कभी-कभी बस खुद को acknowledge करना कि यह कितना matter करता है — यही पहला real step है",
        ]
      },
      "action": {
        "en": [
          "Before talking to the other person, write down what you actually feel and what you actually need — not what you want them to do, what you need",
          "Say one true thing to the person. Not everything — one thing. That's where real conversations start",
        ],
        "hi": [
          "दूसरे से बात करने से पहले लिखो — actually क्या feel करते हो और actually क्या चाहिए — उन्हें क्या करना है नहीं, तुम्हें क्या चाहिए",
          "उस इंसान को एक सच्ची बात कहो। सब नहीं — एक बात। real conversations यहीं से शुरू होती हैं",
        ]
      },
      "reflective": {
        "en": [
          "What do you actually need from this relationship — not what you wish it was, but what you actually need it to be?",
          "Are you trying to fix the relationship or trying to be understood? Those need different conversations",
        ],
        "hi": [
          "इस relationship से actually क्या चाहिए — वो नहीं जो चाहते हो कि हो, बल्कि actually क्या होना चाहिए?",
          "क्या relationship fix करने की कोशिश है या समझे जाने की? यह अलग conversations हैं",
        ]
      }
    },
    "deep": {
      "reflective": {
        "en": [
          "What does this relationship bring out in you — your best self, or a version you don't recognize?",
          "Are you staying because it's genuinely good, or because leaving feels impossible? Those are very different reasons",
          "What pattern do you see repeating across your relationships? Patterns have roots — knowing the root is what changes the pattern",
        ],
        "hi": [
          "यह relationship तुम्हारे अंदर क्या bring out करती है — तुम्हारा best self, या एक version जो तुम खुद नहीं पहचानते?",
          "क्या इसलिए रुके हो क्योंकि genuinely अच्छा है, या क्योंकि जाना impossible लगता है? यह बहुत अलग reasons हैं",
          "अपनी relationships में कौन सा pattern repeat होता देखते हो? patterns की जड़ें होती हैं — जड़ जानने से ही pattern बदलता है",
        ]
      }
    },
    "simple": {
      "action": {
        "en": ["Write what you wish the other person understood — just for yourself, not to send. That clarity helps"],
        "hi": ["लिखो कि चाहते हो वो इंसान क्या समझे — सिर्फ अपने लिए, send नहीं करना। यह clarity help करती है"]
      }
    },
    "next": {
      "action": {
        "en": ["Right now: write one sentence about what you need. Not what you want them to do — what you need. Start there"],
        "hi": ["अभी: एक sentence लिखो कि क्या चाहिए। उन्हें क्या करना है नहीं — तुम्हें क्या चाहिए। यहाँ से शुरू करो"]
      }
    }
  },

  # ───────────────────────────────────────────────────────────────────────────
  "SocialAnxiety": {

    "normal": {
      "emotional": {
        "en": [
          "The fear of being judged is one of the most exhausting things to carry — because it never fully switches off. You're not being oversensitive. This is real and it's heavy",
          "Social anxiety isn't shyness. It's your nervous system treating social situations like threats. That's not a character flaw — it's a pattern that formed for a reason",
          "Dreading a conversation before it happens, replaying it after — that mental load is genuinely tiring. You're not imagining it",
        ],
        "hi": [
          "लोगों के judge करने का डर सबसे थका देने वाली चीज़ों में से एक है — क्योंकि यह कभी पूरी तरह बंद नहीं होता। तुम ज़्यादा sensitive नहीं हो। यह real है और heavy है",
          "Social anxiety सिर्फ shyness नहीं है। यह तुम्हारा nervous system है जो social situations को threat की तरह treat करता है। यह character flaw नहीं — यह एक pattern है जो किसी वजह से बना",
          "बात होने से पहले उसे dread करना, बाद में replay करना — यह mental load genuinely थका देता है। तुम imagine नहीं कर रहे",
        ]
      },
      "analytical": {
        "en": [
          "Social anxiety runs on a loop: anticipate → dread → avoid → feel relieved → repeat. The relief from avoiding is what keeps the loop going. Avoidance feeds it",
          "The judgment you fear is almost always more severe in your imagination than in reality. Most people are thinking about themselves, not watching you",
          "Notice the pattern: is the anxiety worst before the situation, during it, or after? Knowing where it peaks tells you where to focus first",
        ],
        "hi": [
          "Social anxiety एक loop पर चलती है: anticipate → dread → avoid → relief feel करो → repeat। Avoid करने की relief ही loop को चलाती रहती है",
          "जिस judgment से डरते हो वो almost हमेशा imagination में reality से कहीं ज़्यादा severe होती है। ज़्यादातर लोग खुद के बारे में सोच रहे होते हैं, तुम्हें नहीं देख रहे",
          "Pattern notice करो: anxiety सबसे ज़्यादा situation से पहले है, उसके दौरान, या बाद में? यह जानना बताता है पहले कहाँ focus करें",
        ]
      },
      "action": {
        "en": [
          "This week: do one small social thing you'd normally avoid — reply to a message, say one thing in a group chat. Not to cure anything. Just to show your brain the threat isn't real",
          "Before the next situation you're dreading: write down the exact worst thing you think will happen. Then write what would actually happen if it did. Usually the real consequence is far smaller than the fear",
          "After a social situation — stop the replay. Give yourself 2 minutes max to reflect, then consciously move to something else. Replaying reinforces anxiety, it doesn't process it",
        ],
        "hi": [
          "इस हफ्ते: एक छोटा social काम करो जो normally avoid करते — किसी message का reply करो, group chat में एक बात कहो। कुछ cure करने के लिए नहीं। बस brain को दिखाने के लिए कि threat real नहीं है",
          "अगली situation से पहले जिससे डर रहे हो: exactly वो worst चीज़ लिखो जो लगता है होगी। फिर लिखो अगर हो भी गई तो actually क्या होगा। Usually real consequence डर से कहीं छोटी होती है",
          "Social situation के बाद — replay बंद करो। खुद को 2 minutes दो reflect करने के लिए, फिर consciously कुछ और करो। Replaying anxiety को process नहीं करती, reinforce करती है",
        ]
      },
      "reflective": {
        "en": [
          "What specifically are you afraid people will think? Try to name it precisely — 'they'll think I'm boring', 'they'll think I'm stupid'. Getting specific makes the fear smaller",
          "When did you first start feeling this way in social situations? Was there a time before this when it felt easier?",
          "Whose voice is it that tells you you'll be judged? Is it actually the people around you — or someone from earlier in your life?",
        ],
        "hi": [
          "Specifically क्या डर है कि लोग क्या सोचेंगे? इसे precisely name करने की कोशिश करो — 'वो सोचेंगे मैं boring हूँ', 'वो सोचेंगे मैं stupid हूँ'। Specific होने से डर छोटा होता है",
          "Social situations में यह कब से feel होने लगा? क्या कोई वक्त था जब यह easier लगता था?",
          "वो आवाज़ किसकी है जो कहती है तुम्हें judge किया जाएगा? क्या वो actually तुम्हारे आसपास के लोग हैं — या ज़िंदगी में पहले कोई था?",
        ]
      },
      "reframe": {
        "en": [
          "Anxiety before social situations is your brain trying to protect you — it's just miscalibrated. The goal isn't to feel no fear. It's to act anyway while the fear is there",
          "Everyone in that room has their own version of self-consciousness running. The person you think is judging you is probably worried about being judged themselves",
          "Feeling nervous before speaking isn't weakness — it means you care. The nervousness and the courage exist at the same time. You don't need the nervousness to disappear to act",
        ],
        "hi": [
          "Social situations से पहले anxiety तुम्हारा brain तुम्हें protect करने की कोशिश है — बस miscalibrated है। Goal कोई डर न feel करना नहीं है। Goal है डर होते हुए भी act करना",
          "उस room में हर कोई अपनी खुद की self-consciousness लेकर बैठा है। जो तुम्हें judge कर रहा है लगता है — वो probably खुद judge होने से डर रहा है",
          "बोलने से पहले nervous feel करना कमज़ोरी नहीं — इसका मतलब है तुम्हें care है। Nervousness और courage एक साथ exist करते हैं। Act करने के लिए nervousness को जाने की ज़रूरत नहीं",
        ]
      },
      "story": {
        "en": [
          "Almost everyone who seems naturally confident in social situations has learned to act despite anxiety — not in the absence of it. Confidence is a practiced behavior, not a personality you either have or don't",
          "The most socially fluent people you know have all said something awkward, been misunderstood, or had a conversation go wrong. They just didn't let it define the next one",
        ],
        "hi": [
          "लगभग हर वो इंसान जो social situations में naturally confident लगता है उसने anxiety के बावजूद act करना सीखा है — उसकी absence में नहीं। Confidence एक practiced behavior है, personality नहीं जो हो या न हो",
          "जो लोग तुम्हें socially fluent लगते हैं उन्होंने भी awkward चीज़ें कही हैं, misunderstood हुए हैं, conversations wrong गई हैं। बस उन्होंने उसे अगली बार define नहीं करने दिया",
        ]
      }
    },

    "deep": {
      "emotional": {
        "en": [
          "Social anxiety often has roots — a time you were embarrassed in front of people, laughed at, or made to feel like your voice didn't matter. The anxiety now is protective, even if it's gone too far",
          "The exhaustion of performing 'okay' in social situations while feeling terrified inside is real. You're carrying something most people around you can't see",
        ],
        "hi": [
          "Social anxiety की अक्सर जड़ें होती हैं — कोई वक्त जब लोगों के सामने embarrass हुए, हँसाए गए, या feel कराया गया कि तुम्हारी आवाज़ matter नहीं करती। अब की anxiety protective है, भले ही ज़रूरत से ज़्यादा हो गई हो",
          "Social situations में अंदर से terrified होते हुए 'okay' perform करने की थकान real है। तुम कुछ ऐसा carry कर रहे हो जो तुम्हारे आसपास के लोग देख नहीं सकते",
        ]
      },
      "reflective": {
        "en": [
          "What would it mean for you if people did judge you? What's the actual fear underneath the fear — rejection, being seen as less-than, not belonging?",
          "Is there a version of you that exists only when no one is watching — more relaxed, more yourself? What would it take to let that version exist around other people too?",
          "Who in your life has ever made you feel fully safe to be yourself? What was different about how they showed up?",
        ],
        "hi": [
          "अगर लोग judge भी कर दें तो तुम्हारे लिए क्या मतलब होगा? डर के नीचे actual डर क्या है — rejection, कम समझे जाने का, belong न करने का?",
          "क्या तुम्हारा एक version है जो सिर्फ तब exist करता है जब कोई नहीं देख रहा — ज़्यादा relaxed, ज़्यादा खुद? उस version को दूसरों के साथ भी exist करने देने के लिए क्या चाहिए होगा?",
          "तुम्हारी ज़िंदगी में किसने कभी तुम्हें पूरी तरह खुद होने के लिए safe feel कराया? उन्होंने जो किया उसमें क्या अलग था?",
        ]
      },
      "reframe": {
        "en": [
          "The self-monitoring that social anxiety creates — watching yourself from the outside, editing before you speak — developed as protection. It kept you safe once. It's just not helping you now",
          "You're not too sensitive. You're not broken. You have a nervous system that learned to treat connection as risk. That can be unlearned — slowly, with practice, not with force",
        ],
        "hi": [
          "Social anxiety जो self-monitoring create करती है — खुद को बाहर से देखना, बोलने से पहले edit करना — यह protection के रूप में develop हुई। एक वक्त तुम्हें safe रखती थी। बस अब help नहीं कर रही",
          "तुम ज़्यादा sensitive नहीं हो। तुम broken नहीं हो। तुम्हारे पास एक nervous system है जिसने connection को risk मानना सीख लिया। यह unlearn हो सकता है — धीरे-धीरे, practice से, ज़बरदस्ती से नहीं",
        ]
      },
      "analytical": {
        "en": [
          "Social anxiety is maintained by two things: anticipatory anxiety (dread before) and post-event processing (replay after). Both are imagination, not reality. The actual event is usually the easiest part",
          "Ask: what's the evidence that people are actually judging me? Not the feeling — the actual evidence. Most of the time there isn't any",
        ],
        "hi": [
          "Social anxiety दो चीज़ों से maintain होती है: anticipatory anxiety (पहले का dread) और post-event processing (बाद में replay)। दोनों imagination हैं, reality नहीं। Actual event usually सबसे easy part होता है",
          "पूछो: evidence क्या है कि लोग actually judge कर रहे हैं? Feeling नहीं — actual evidence। ज़्यादातर बार होती ही नहीं",
        ]
      },
      "story": {
        "en": [
          "Social anxiety shrinks your world gradually — fewer situations, smaller circles, more safety. The problem is the world keeps shrinking. Every avoided situation tells your brain the threat was real",
        ],
        "hi": [
          "Social anxiety तुम्हारी दुनिया धीरे-धीरे छोटी करती है — कम situations, छोटे circles, ज़्यादा safety। Problem यह है कि दुनिया सिकुड़ती रहती है। हर avoid की गई situation brain को बताती है कि threat real था",
        ]
      },
      "action": {
        "en": [
          "Write about the last time social anxiety stopped you from doing something you wanted to do. What was the cost? Not the avoided discomfort — the actual cost to your life",
        ],
        "hi": [
          "उस आखिरी बार के बारे में लिखो जब social anxiety ने तुम्हें कुछ ऐसा करने से रोका जो तुम करना चाहते थे। Cost क्या थी? Avoid की गई discomfort नहीं — तुम्हारी ज़िंदगी की actual cost",
        ]
      }
    },

    "simple": {
      "emotional": {
        "en": ["You don't have to perform today. Just show up as you are"],
        "hi": ["आज perform नहीं करना। बस जैसे हो वैसे रहो"]
      },
      "action": {
        "en": ["One small thing: make brief eye contact and smile at one person today. That's it"],
        "hi": ["एक छोटी चीज़: आज एक इंसान से brief eye contact करो और smile करो। बस इतना"]
      },
      "reframe": {
        "en": ["They're not watching as closely as it feels. Everyone is mostly inside their own head"],
        "hi": ["वो उतना नहीं देख रहे जितना feel होता है। हर कोई mostly अपने ही दिमाग में है"]
      }
    },

    "next": {
      "action": {
        "en": ["Right now: do the one small social thing you've been avoiding. Text back, say the thing, show up. Ten seconds of courage"],
        "hi": ["अभी: वो एक छोटा social काम करो जो avoid कर रहे थे। Text back करो, वो बात कहो, show up करो। दस seconds की हिम्मत"]
      }
    }
  }

}

# ─────────────────────────────────────────────────────────────────────────────
#  CONTEXT-AWARE FOLLOW-UP BRIDGES
#  When session has history, prepend a bridge line that references it
# ─────────────────────────────────────────────────────────────────────────────

BRIDGES = {
  "deep": {
    "en": [
      "Going deeper on what you shared —",
      "Building on what you said —",
      "Let's sit with this a bit more —",
    ],
    "hi": [
      "जो share किया उस पर थोड़ा और गहरे जाते हैं —",
      "जो बताया उसे आगे बढ़ाते हैं —",
      "इसे थोड़ा और feel करते हैं —",
    ]
  },
  "next": {
    "en": [
      "One concrete thing you can do right now —",
      "From everything you've shared, the clearest next step —",
    ],
    "hi": [
      "अभी एक concrete काम जो कर सकते हो —",
      "जो share किया उसमें से, सबसे clear अगला कदम —",
    ]
  },
  "simple": {
    "en": [
      "Stripping it all back to the simplest version —",
      "Let's make this as simple as possible —",
    ],
    "hi": [
      "इसे सबसे simple version में लाते हैं —",
      "इसे जितना simple हो सके करते हैं —",
    ]
  }
}

FALLBACK = {
  "normal": {"en": ["Take one small step toward what matters to you today"], "hi": ["आज एक छोटा कदम उठाओ उस चीज़ की तरफ जो matter करती है"]},
  "deep":   {"en": ["Ask yourself what you truly want underneath all of this"], "hi": ["खुद से पूछो इस सब के नीचे तुम सच में क्या चाहते हो"]},
  "simple": {"en": ["One small thing. Right now. That's all"], "hi": ["एक छोटी चीज़। अभी। बस इतना"]},
  "next":   {"en": ["Right now: write down the one thing you need to do first"], "hi": ["अभी: वो एक चीज़ लिखो जो सबसे पहले करनी है"]},
}

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _load_negative_intents():
    neg = set()
    if os.path.exists("feedback_data.json"):
        try:
            with open("feedback_data.json", "r") as f:
                for e in json.load(f):
                    if e.get("feedback") == "no":
                        neg.add(e.get("intent"))
        except Exception:
            pass
    return neg

def _pick(pool, lang, n=1):
    """Pick n random items from pool[lang], fallback to 'en'."""
    items = pool.get(lang) or pool.get("en", [])
    if not items:
        return []
    return random.sample(items, min(n, len(items)))

def _get_type_for_session(history, mode):
    """
    Choose response type based on conversation history.
    Avoids repeating the same type twice in a row.
    """
    if not history:
        # First message: lead with emotional acknowledgment
        return random.choice(["emotional", "analytical", "reframe"])

    last_type = history[-1].get("response_type", "")
    # Don't repeat same type
    available = [t for t in RESPONSE_TYPES if t != last_type]

    if mode == "deep":
        preferred = ["reflective", "emotional", "story", "reframe"]
    elif mode == "simple":
        preferred = ["emotional", "action", "reframe"]
    elif mode == "next":
        preferred = ["action"]
    else:
        preferred = available

    candidates = [t for t in preferred if t in available]
    return random.choice(candidates) if candidates else random.choice(available)

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def generate_action_plan(detected_intents, confidence, mood, lang="en",
                         mode="normal", user_input="", history=None):
    """
    Returns list of step strings — same structure, displayed as bullets.
    history: list of session memory dicts from app.py
    """
    if history is None:
        history = []

    steps = []
    neg = _load_negative_intents()

    # 1. Context bridge for follow-ups
    is_followup = len(history) > 1
    if is_followup and mode in BRIDGES:
        bridge_pool = BRIDGES[mode]
        steps += _pick(bridge_pool, lang, 1)

    # 2. Low confidence note — only when truly uncertain
    if confidence < 40:
        steps.append(
            "I'm not fully certain — tell me more if this doesn't feel right"
            if lang == "en"
            else "पूरी तरह sure नहीं — अगर सही नहीं लगा तो थोड़ा और बताओ"
        )

    # 3. Pick primary intent
    primary = None
    for name, _ in detected_intents:
        if name not in neg and name in BANK:
            primary = name
            break
    if not primary and detected_intents:
        primary = detected_intents[0][0]

    # 4. Pick response type based on conversation history
    response_type = _get_type_for_session(history, mode)

    # 5. Get content from bank
    intent_bank = BANK.get(primary, {})
    mode_bank   = intent_bank.get(mode) or intent_bank.get("normal") or {}
    type_pool   = mode_bank.get(response_type) or {}

    if type_pool:
        n = {"normal": 3, "deep": 3, "simple": 2, "next": 1}.get(mode, 3)
        steps += _pick(type_pool, lang, n)
    else:
        # Try any type in this mode
        for t in RESPONSE_TYPES:
            pool = mode_bank.get(t, {})
            if pool:
                n = {"normal": 3, "deep": 3, "simple": 2, "next": 1}.get(mode, 3)
                steps += _pick(pool, lang, n)
                break

    # Fallback
    if len(steps) <= 1:
        fb = FALLBACK.get(mode, FALLBACK["normal"])
        steps += fb.get(lang) or fb["en"]

    # 6. Deduplicate + cap
    steps = list(dict.fromkeys(steps))
    cap = {"normal": 4, "deep": 4, "simple": 3, "next": 2}.get(mode, 4)
    return steps[:cap], response_type   # return type so app.py can store it