# -*- coding: utf-8 -*-
"""
lexicon_data.py - Cơ sở dữ liệu từ vựng, phiên âm IPA, loại từ, nghĩa tiếng Việt,
phân loại chủ đề và từ dễ nhầm cho 15 Unit của English Discoveries Intermediate 2 & 3.
"""

UNIT_TOPICS = {
    "I2-U01": {
        "title": "Mua sắm & Sở hữu Xe hơi (Buying A Used Car / Cars)",
        "theme_categories": {
            "Mua bán & Giá cả": ["bargain", "great deal", "reasonable prices", "down payment", "monthly payments", "affordable", "dealer", "salesperson"],
            "Loại xe & Tính năng": ["brand-new", "used cars", "economy-sized", "luxury models", "automatic gearshift", "extra features", "latest model", "tires"],
            "Bảo dưỡng & Trạng thái": ["break down", "oil leak", "have work done", "mechanic", "satisfied with", "guarantee"]
        },
        "confusing_words": [
            ("- **used car** (xe đã qua sử dụng / xe cũ) vs **second-hand** (đồ cũ nói chung): Cả hai đều chỉ đồ cũ, nhưng 'used car' là thuật ngữ thương mại chuẩn xác nhất trong ngành mua bán xe."),
            ("- **down payment** (khoản tiền trả trước khi mua trả góp) vs **installment** (khoản tiền trả từng đợt hàng tháng): Cần phân biệt rõ để tránh nhầm lẫn khi đàm phán phương thức thanh toán."),
            ("- **bargain** (n: món hời / v: mặc cả, trả giá) vs **discount** (khoản tiền được giảm trực tiếp trên giá niêm yết)."),
            ("- **guarantee** (bảo đảm, cam kết chất lượng của hãng) vs **warranty** (phiếu bảo hành sửa chữa miễn phí khi có sự cố).")
        ]
    },
    "I2-U02": {
        "title": "Tai nạn & Cứu nạn Vực hiểm (Accidents & Cliff Rescue)",
        "theme_categories": {
            "Địa hình hiểm trở & Sự cố": ["cliff", "rocky", "slippery", "take a wrong turn", "get stuck", "left behind"],
            "Cảm xúc & Tâm lý": ["afraid", "terror", "panic", "scared"],
            "Y tế, Chấn thương & Cứu hộ": ["rescue", "injury", "bleeding", "recover", "paramedic", "first aid"]
        },
        "confusing_words": [
            ("- **afraid** (adj: sợ hãi, e sợ - dùng sau to be: be afraid of) vs **fear** (n/v: nỗi sợ, sợ hãi). Không nói 'an afraid person' mà dùng 'a frightened person'."),
            ("- **injury** (chấn thương thể xác do tai nạn, va đập) vs **wound** (vết thương hở do vũ khí, dao kéo đâm chém) vs **pain** (cảm giác đau đớn)."),
            ("- **slippery** (trơn trượt - tính từ miêu tả bề mặt) vs **slide** (trượt - động từ hành động)."),
            ("- **recover** (hồi phục sức khỏe sau chấn thương / tìm lại đồ mất) vs **cure** (chữa khỏi hoàn toàn bệnh lý).")
        ]
    },
    "I2-U03": {
        "title": "Gia đình, Mối quan hệ & Tiệc tùng (Family & Social Gatherings)",
        "theme_categories": {
            "Mối quan hệ & Giao tiếp xã hội": ["acquaintances", "in common", "hold a conversation", "gossip", "insult", "run into"],
            "Chuẩn bị dự tiệc": ["attend a party", "get dressed", "have your hair done", "show up", "impress"],
            "Quy tắc & Thái độ ứng xử": ["part of the game", "foreign affair", "relative", "manners"]
        },
        "confusing_words": [
            ("- **acquaintance** (người quen - chỉ biết mặt, nói chuyện vài lần) vs **friend** (bạn bè thân thiết) vs **colleague** (đồng nghiệp tại nơi làm việc)."),
            ("- **gossip** (ngồi lê đôi mách, bàn tán chuyện đời tư người khác sau lưng) vs **rumor** (tin đồn vô căn cứ chưa được xác thực)."),
            ("- **insult** (v/n: sỉ nhục, xúc phạm thẳng thừng) vs **compliment** (lời khen ngợi, tán dương)."),
            ("- **show up** (phr v: xuất hiện, có mặt tại cuộc hẹn / bữa tiệc) vs **turn up** (xuất hiện bất ngờ hoặc tăng âm lượng).")
        ]
    },
    "I2-U04": {
        "title": "Hàng xóm & Sửa chữa Nhà cửa (Neighborhood & Home Repairs)",
        "theme_categories": {
            "Sửa chữa & Thiết bị gia dụng": ["damage", "leak", "replacement part", "repair", "handyman", "furnace", "home repairs"],
            "Quan hệ lối xóm & Ứng xử": ["welcome", "neighbor", "neighborhood", "borrow", "favor", "advice", "hint"],
            "Kiểm tra & Thay đổi": ["check", "redecorate", "maintenance", "tenant"]
        },
        "confusing_words": [
            ("- **borrow** (mượn - nhận cái gì từ ai có sự cho phép và sẽ trả lại: borrow sth from sb) vs **lend** (cho mượn: lend sth to sb)."),
            ("- **repair** (sửa chữa đồ hỏng cho hoạt động lại) vs **redecorate** (trang hoàng, sơn sửa lại nội thất cho đẹp hơn)."),
            ("- **damage** (danh từ không đếm được: sự hư hại, tổn thất) vs **damages** (số nhiều: tiền bồi thường thiệt hại theo luật pháp)."),
            ("- **advice** (danh từ không đếm được: lời khuyên - không dùng 'an advice') vs **advise** (động từ: khuyên nhủ).")
        ]
    },
    "I2-U05": {
        "title": "Thăng tiến Công việc & Tính từ Miêu tả (Career & Descriptive Adjectives)",
        "theme_categories": {
            "Tính cách & Ứng xử": ["polite", "rude", "bothersome", "tough", "disappointed"],
            "Phong cách & Vẻ ngoài": ["elegant", "glamorous", "tiny", "deep", "full", "loud"],
            "Môi trường & Không gian": ["deserted", "promotion", "assignment", "workplace"]
        },
        "confusing_words": [
            ("- **polite** (lịch sự, có văn hóa) vs **rude** (thô lỗ, mất lịch sự). Từ đồng nghĩa của polite: courteous; từ đồng nghĩa của rude: impolite, discourteous."),
            ("- **elegant** (thanh lịch, trang nhã tinh tế) vs **glamorous** (quyến rũ, hào nhoáng, lộng lẫy cuốn hút)."),
            ("- **deserted** (vắng vẻ, không một bóng người - miêu tả nơi chốn) vs **desert** (danh từ: sa mạc / động từ: bỏ rơi)."),
            ("- **bothersome** (phiền toái, gây bực mình khó chịu) vs **annoyed** (cảm giác bực mình của con người).")
        ]
    },
    "I2-U06": {
        "title": "Tài chính Cá nhân & Chi tiêu Thông minh (Personal Finance)",
        "theme_categories": {
            "Tình trạng tài chính": ["wealthy", "short of cash", "limited budget", "affordable", "satisfied"],
            "Giao dịch & Thanh toán": ["purchase", "installments", "down payment", "bargain", "brand-new"],
            "Giá trị & Bảo đảm": ["get your money's worth", "guarantee", "investment", "raise"]
        },
        "confusing_words": [
            ("- **wealthy** (giàu có, nhiều tài sản tích lũy) vs **rich** (giàu có, nhiều tiền). 'Wealthy' thể hiện sự giàu sang bền vững hơn."),
            ("- **affordable** (giá cả phải chăng, vừa túi tiền đối với người mua) vs **cheap** (rẻ tiền - đôi khi mang sắc thái chất lượng kém)."),
            ("- **installment** (khoản tiền trả góp theo kỳ) vs **interest** (tiền lãi phát sinh khi vay mượn hoặc mua trả góp)."),
            ("- **short of cash** (thiếu tiền mặt tạm thời) vs **broke** (cháy túi, hoàn toàn không còn tiền).")
        ]
    },
    "I2-U07": {
        "title": "Chính trị & Chiến dịch Bầu cử (Politics & Election Campaigns)",
        "theme_categories": {
            "Bầu cử & Ứng cử viên": ["candidate", "election", "run for office", "vote", "the vote is in", "elect", "voters", "election results"],
            "Chiến dịch & Thăm dò": ["campaign", "lead in the polls", "poll", "controversial issues", "press conference", "chances", "party"],
            "Kết quả & Thẩm quyền": ["defeat", "mayor", "speech", "politics", "manager"]
        },
        "confusing_words": [
            ("- **candidate** (ứng cử viên tham gia tranh cử) vs **nominee** (người được đề cử chính thức bởi một đảng phái)."),
            ("- **defeat** (v: đánh bại đối thủ / n: sự thất bại) vs **win** (chiến thắng). Tránh nhầm lẫn tân ngữ: defeat sb (đánh bại ai) vs win a prize/election (chiến thắng giải/bầu cử)."),
            ("- **poll** (cuộc thăm dò dư luận / phòng bỏ phiếu) vs **vote** (lá phiếu / hành động bỏ phiếu)."),
            ("- **politics** (n: chính trị - luôn có -s nhưng là danh từ số ít) vs **policy** (chính sách, chủ trương cụ thể).")
        ]
    },
    "I2-U08": {
        "title": "Tội phạm, Thời tiết & Du lịch (Crime, Law & Travel)",
        "theme_categories": {
            "Tội ác & Hành vi phạm pháp": ["arson", "murder", "commit", "illegal", "threat"],
            "Điều tra & Pháp y": ["clue", "evidence", "inspection", "open an investigation", "suspicion", "suspect"],
            "Thời tiết & Chuyến bay": ["forecast", "flight information", "would you mind", "delay"]
        },
        "confusing_words": [
            ("- **arson** (tội cố ý phóng hỏa đốt phá tài sản) vs **fire** (ngọn lửa / vụ cháy nói chung do tai nạn)."),
            ("- **evidence** (chứng cứ xác thực được tòa án công nhận - danh từ không đếm được) vs **clue** (manh mối, gợi ý giúp lần ra manh mối trong cuộc điều tra)."),
            ("- **suspect** (n: /ˈsʌspekt/ nghi phạm / v: /səˈspekt/ nghi ngờ) vs **suspicion** (n: sự nghi ngờ, linh cảm)."),
            ("- **commit a crime** (phạm tội - luôn dùng động từ 'commit', không dùng 'make' hay 'do').")
        ]
    },
    "I2-U09": {
        "title": "Bảo vệ Môi trường & Tái chế (Recycling & Upcycling)",
        "theme_categories": {
            "Phương pháp xử lý rác": ["recycle", "reuse", "upcycle", "biodegradable", "sorting", "separate"],
            "Vấn đề môi trường & Rác thải": ["waste", "landfill", "pollution", "natural resources", "scrap"],
            "Cộng đồng & Giáo dục": ["workshop", "hands-on", "survey", "preservation", "lecture"]
        },
        "confusing_words": [
            ("- **recycle** (tái chế - xử lý rác thải thành nguyên liệu thô để sản xuất sản phẩm mới) vs **upcycle** (tái chế sáng tạo - biến đồ bỏ đi thành vật dụng có giá trị thẩm mỹ hoặc công năng cao hơn) vs **reuse** (tái sử dụng nguyên trạng đồ vật)."),
            ("- **biodegradable** (có thể phân hủy sinh học tự nhiên) vs **recyclable** (có thể tái chế được)."),
            ("- **waste** (rác thải, sự lãng phí) vs **scrap** (phế liệu, mảnh vụn kim loại/vải thừa có thể tái chế)."),
            ("- **landfill** (bãi rác chôn lấp tập trung) vs **bin** (thùng rác công cộng/gia đình).")
        ]
    },
    "I2-U10": {
        "title": "Công nghiệp Điện ảnh & Làm phim (Movie Making & Film Industry)",
        "theme_categories": {
            "Sản xuất & Đoàn làm phim": ["film set", "director", "cameraman", "scene", "production", "cinematography"],
            "Hậu kỳ & Công nghệ số": ["digital technology", "special effects", "sound engineer", "editing", "animation"],
            "Phát hành & Đào tạo": ["film festival", "documentary", "movie industry", "film school", "independent films"]
        },
        "confusing_words": [
            ("- **documentary** (phim tài liệu phản ánh sự thật) vs **feature film** (phim truyện hư cấu chiếu rạp)."),
            ("- **director** (đạo diễn nghệ thuật chịu trách nhiệm chỉ đạo diễn xuất và hình ảnh) vs **producer** (nhà sản xuất phụ trách tài chính, nhân sự và tổ chức)."),
            ("- **scene** (cảnh quay diễn ra tại một địa điểm, thời gian cụ thể) vs **shot** (cú máy quay liên tục không ngắt)."),
            ("- **props** (đạo cụ cầm tay của diễn viên) vs **costume** (trang phục nhân vật).")
        ]
    },
    "I3-U01": {
        "title": "Mối quan hệ & Tình cảm (Interpersonal Relationships)",
        "theme_categories": {
            "Hẹn hò & Tình yêu": ["in love with", "get engaged", "blind date", "flirt", "embrace", "affectionate"],
            "Hôn nhân & Thay đổi": ["get divorced", "divorced", "spending time", "get used to"],
            "Tính cách & Giao lưu": ["easygoing", "sense of humor", "tease", "acquaintance"]
        },
        "confusing_words": [
            ("- **get engaged** (đính hôn, hứa hôn) vs **get married** (kết hôn, làm đám cưới) vs **get divorced** (ly hôn)."),
            ("- **easygoing** (tính tình dễ gần, thoải mái, không khắt khe) vs **careless** (bất cẩn, cẩu thả)."),
            ("- **blind date** (cuộc hẹn hò gián tiếp với người chưa từng gặp mặt) vs **date** (buổi hẹn hò thông thường)."),
            ("- **affectionate** (giàu tình cảm, hay âu yếm thể hiện tình yêu) vs **effective** (hiệu quả, có tác dụng).")
        ]
    },
    "I3-U02": {
        "title": "Thể thao, Thể lực & Sức khỏe (Sports & Athletics)",
        "theme_categories": {
            "Tập luyện & Thể lực": ["in shape", "condition", "build up your strength", "weight lifting", "at your own pace"],
            "Thi đấu & Tinh thần": ["finals", "team spirit", "make a name for yourself", "handle an upset", "give in"],
            "Cơ sở vật chất & Trạng thái": ["well-equipped", "exhausted", "college sports", "athlete"]
        },
        "confusing_words": [
            ("- **in shape** (có thể lực tốt, vóc dáng cân đối săn chắc) vs **out of shape** (yếu ớt, cơ thể thiếu vận động)."),
            ("- **give in** (phr v: chịu thua, nhượng bộ, đầu hàng đối phương) vs **give up** (từ bỏ một thói quen hoặc mục tiêu)."),
            ("- **finals** (loạt trận chung kết tranh cúp vô địch) vs **semi-finals** (trận bán kết)."),
            ("- **exhausted** (cực kỳ kiệt sức, mệt lử) vs **tired** (mệt mỏi thông thường).")
        ]
    },
    "I3-U03": {
        "title": "Quan hệ Lao động & Đình công (Labor Relations & Workplace Rights)",
        "theme_categories": {
            "Đấu tranh & Quyền lợi": ["go on strike", "walk out", "wage increase", "incentives", "proposal"],
            "Xử lý khủng hoảng": ["handle the situation", "empty promise", "under the circumstances", "make cuts"],
            "Công việc & Năng suất": ["productive", "quit", "make a living", "labor relations"]
        },
        "confusing_words": [
            ("- **go on strike** (bãi công, đình công tập thể đòi quyền lợi) vs **quit** (tự nguyện đơn phương nghỉ việc)."),
            ("- **wage** (tiền lương trả theo giờ hoặc theo tuần cho lao động chân tay) vs **salary** (tiền lương cố định hàng tháng cho nhân viên văn phòng)."),
            ("- **make cuts** (cắt giảm ngân sách, nhân sự hoặc chi tiêu) vs **lay off** (sa thải công nhân do công ty thu hẹp sản xuất)."),
            ("- **productive** (đạt năng suất cao, hoàn thành nhiều việc) vs **busy** (bận rộn nhưng chưa chắc đã hiệu quả).")
        ]
    },
    "I3-U04": {
        "title": "Các vấn đề Xã hội & Người vô gia cư (Social Problems & Homelessness)",
        "theme_categories": {
            "Tình trạng vô gia cư & Khó khăn": ["homeless", "on the streets", "housing alternatives", "pay the rent"],
            "Trợ cấp & Trách nhiệm cộng đồng": ["make a difference", "take steps", "senior citizen", "manage by yourself"],
            "Xã hội & Thể chế": ["controversial issues", "establishment", "capable of", "depend on"]
        },
        "confusing_words": [
            ("- **homeless** (không có nhà ở, vô gia cư) vs **helpless** (bất lực, không có khả năng tự xoay xở). Bài học phân biệt rõ 'Does homeless mean helpless?' - người vô gia cư không có nghĩa là người bất lực."),
            ("- **depend on** (phụ thuộc hoặc trông cậy vào ai) vs **independent** (độc lập, tự chủ)."),
            ("- **senior citizen** (cụ già, công dân cao tuổi từ 65 tuổi trở lên - cách nói trang trọng lịch sự) vs **old person** (cách nói thông tục)."),
            ("- **establishment** (giới quyền lực, các cơ quan ban ngành đầu não) vs **organization** (tổ chức nói chung).")
        ]
    },
    "I3-U05": {
        "title": "Sức khỏe, Tim mạch & Dinh dưỡng (Health, Nutrition & Heart Attack)",
        "theme_categories": {
            "Bệnh lý tim mạch & Triệu chứng": ["heart attack", "heart condition", "palpitations", "sweating"],
            "Chế độ ăn & Kiểm soát cân nặng": ["eat sensibly", "whole-grain", "nutritious", "small quantities", "limit", "overweight", "weigh yourself"],
            "Lối sống & Thể chất": ["concentrate on", "recovery", "healthy diet", "prevention"]
        },
        "confusing_words": [
            ("- **heart attack** (nhồi máu cơ tim - hiện tượng tim đột ngột ngừng hoạt động hoặc thiếu máu cục bộ cấp tính) vs **heart disease / heart condition** (bệnh tim mãn tính nói chung)."),
            ("- **overweight** (thừa cân - vượt mức tiêu chuẩn thông thường) vs **obese** (béo phì - tình trạng bệnh lý nguy hiểm do tích tụ quá nhiều mỡ thừa)."),
            ("- **palpitations** (chứng tim đập nhanh, đánh trống ngực dồn dập bất thường) vs **pulse / heart rate** (nhịp tim sinh lý bình thường)."),
            ("- **whole-grain** (ngũ cốc nguyên cám, giữ nguyên vẹn chất xơ và vi chất) vs **refined grain** (ngũ cốc tinh chế đã xay xát bỏ vỏ cám).")
        ]
    }
}

LEXICON_DB = {
    # Unit 1
    "break down": ("Cụm động từ", "/breɪk daʊn/", "Hỏng hóc, chết máy (xe)"),
    "oil leak": ("Cụm danh từ", "/ɔɪl liːk/", "Hiện tượng rò rỉ dầu nhớt"),
    "economy-sized": ("Tính từ", "/ɪˈkɑːnəmi saɪzd/", "Cỡ tiết kiệm, nhỏ gọn ít tốn xăng"),
    "latest model": ("Cụm danh từ", "/ˈleɪtɪst ˈmɑːdl/", "Mẫu xe đời mới nhất"),
    "dealer": ("Danh từ", "/ˈdiːlər/", "Người bán xe, đại lý ô tô"),
    "tires": ("Danh từ số nhiều", "/ˈtaɪərz/", "Lốp xe ô tô/xe đạp"),
    "extra features": ("Cụm danh từ", "/ˈekstrə ˈfiːtʃərz/", "Các tính năng bổ sung cao cấp"),
    "automatic gearshift": ("Cụm danh từ", "/ˌɔːtəˈmætɪk ˈɡɪrʃɪft/", "Hộp số tự động, cần số tự động"),
    "used car": ("Cụm danh từ", "/juːzd kɑːr/", "Xe ô tô cũ, xe đã qua sử dụng"),
    "used cars": ("Cụm danh từ", "/juːzd kɑːrz/", "Các xe ô tô cũ, đã qua sử dụng"),
    "great deal": ("Cụm danh từ", "/ɡreɪt diːl/", "Món hời lớn, giá rất tốt"),
    "have work done": ("Thành ngữ", "/hæv wɜːrk dʌn/", "Mang xe đi sửa chữa, tân trang"),
    "luxury": ("Danh từ / Tính từ", "/ˈlʌkʃəri/", "Sang trọng, xa xỉ, cao cấp"),
    "luxury models": ("Cụm danh từ", "/ˈlʌkʃəri ˈmɑːdlz/", "Các mẫu xe sang trọng, cao cấp"),
    "bargain": ("Danh từ", "/ˈbɑːrɡən/", "Món hời, giá rẻ bất ngờ"),
    "fantastic bargains": ("Cụm danh từ", "/fænˈtæstɪk ˈbɑːrɡənz/", "Những món hời tuyệt vời, giảm giá sâu"),
    "brand-new": ("Tính từ", "/ˌbrænd ˈnuː/", "Mới toanh, mới nguyên 100%"),
    "down payment": ("Cụm danh từ", "/ˈdaʊn ˌpeɪmənt/", "Khoản tiền trả trước (đặt cọc trước)"),
    "monthly payments": ("Cụm danh từ", "/ˈmʌnθli ˈpeɪmənts/", "Tiền trả góp định kỳ hàng tháng"),
    "guarantee": ("Động từ / Danh từ", "/ˌɡærənˈtiː/", "Bảo đảm, cam kết chất lượng"),
    "mechanic": ("Danh từ", "/məˈkænɪk/", "Thợ máy sửa chữa ô tô"),
    "reasonable prices": ("Cụm danh từ", "/ˈriːznəbl ˈpraɪsɪz/", "Mức giá hợp lý, phải chăng"),
    "satisfied with": ("Cụm tính từ", "/ˈsætɪsfaɪd wɪð/", "Hài lòng, vừa ý với cái gì"),
    "recommend": ("Động từ", "/ˌrekəˈmend/", "Giới thiệu, khuyên dùng"),
    "have in mind": ("Thành ngữ", "/hæv ɪn maɪnd/", "Có ý định trong đầu, dự tính"),
    "make up your mind": ("Thành ngữ", "/meɪk ʌp jɔːr maɪnd/", "Đưa ra quyết định dứt khoát"),
    "bargaining": ("Danh từ / Động từ", "/ˈbɑːrɡənɪŋ/", "Việc mặc cả, trả giá"),
    "method of payment": ("Cụm danh từ", "/ˈmeθəd əv ˈpeɪmənt/", "Phương thức thanh toán"),
    "lower the price": ("Thành ngữ", "/ˈloʊər ðə praɪs/", "Hạ giá, giảm giá bán"),
    "salesperson": ("Danh từ", "/ˈseɪlzpɜːrsn/", "Nhân viên bán hàng"),
    "customer": ("Danh từ", "/ˈkʌstəmər/", "Khách hàng mua sắm"),
    "showroom": ("Danh từ", "/ˈʃoʊruːm/", "Phòng trưng bày sản phẩm/xe"),

    # Unit 2
    "afraid": ("Tính từ", "/əˈfreɪd/", "Sợ hãi, e sợ"),
    "cliff": ("Danh từ", "/klɪf/", "Vách đá, bờ vực hiểm trở"),
    "left behind": ("Cụm động từ", "/left bɪˈhaɪnd/", "Bị bỏ lại phía sau"),
    "rescue": ("Động từ / Danh từ", "/ˈreskjuː/", "Giải cứu, cứu nạn"),
    "slippery": ("Tính từ", "/ˈslɪpəri/", "Trơn trượt, dễ ngã"),
    "take a wrong turn": ("Thành ngữ", "/teɪk ə rɔːŋ tɜːrn/", "Rẽ nhầm đường, đi lạc lối"),
    "bleeding": ("Danh từ / Động từ", "/ˈbliːdɪŋ/", "Chảy máu, mất máu"),
    "injury": ("Danh từ", "/ˈɪndʒəri/", "Vết thương, chấn thương thân thể"),
    "recover": ("Động từ", "/rɪˈkʌvər/", "Bình phục, hồi phục sức khỏe"),
    "rocky": ("Tính từ", "/ˈrɑːki/", "Gồ ghề, đầy đá tảng lởm chởm"),
    "get stuck": ("Cụm động từ", "/ɡet stʌk/", "Bị kẹt lại, không di chuyển được"),
    "terror": ("Danh từ", "/ˈterər/", "Nỗi kinh hoàng, sự sợ hãi tột cùng"),
    "steep": ("Tính từ", "/stiːp/", "Dốc đứng, hiểm trở"),
    "paramedic": ("Danh từ", "/ˌpærəˈmedɪk/", "Nhân viên cứu thương y tế khẩn cấp"),

    # Unit 3
    "acquaintances": ("Danh từ số nhiều", "/əˈkweɪntənsɪz/", "Người quen biết sơ sơ (chưa phải bạn thân)"),
    "acquaintance": ("Danh từ", "/əˈkweɪntəns/", "Người quen biết"),
    "get dressed": ("Cụm động từ", "/ɡet drest/", "Mặc quần áo, diện đồ"),
    "have your hair done": ("Thành ngữ", "/hæv jɔːr her dʌn/", "Đi làm tóc, tạo kiểu tóc ở tiệm"),
    "impress": ("Động từ", "/ɪmˈpres/", "Gây ấn tượng sâu sắc"),
    "in common": ("Thành ngữ", "/ɪn ˈkɑːmən/", "Có điểm tương đồng, cùng sở thích"),
    "show up": ("Cụm động từ", "/ʃoʊ ʌp/", "Xuất hiện, có mặt tại cuộc hẹn"),
    "run into": ("Cụm động từ", "/rʌn ˈɪntuː/", "Tình cờ bắt gặp, chạm trán ai"),
    "part of the game": ("Thành ngữ", "/pɑːrt əv ðə ɡeɪm/", "Một phần tất yếu của cuộc chơi / cuộc sống"),
    "insult": ("Động từ / Danh từ", "/ɪnˈsʌlt/", "Lăng mạ, xúc phạm, làm tổn thương"),
    "hold a conversation": ("Thành ngữ", "/hoʊld ə ˌkɑːnvərˈseɪʃn/", "Duy trì cuộc trò chuyện"),
    "gossip": ("Động từ / Danh từ", "/ˈɡɑːsɪp/", "Ngồi lê đôi mách, bàn tán chuyện người khác"),
    "attend a party": ("Thành ngữ", "/əˈtend ə ˈpɑːrti/", "Tham dự một bữa tiệc"),

    # Unit 4
    "advice": ("Danh từ", "/ədˈvaɪs/", "Lời khuyên, sự chỉ dẫn bổ ích"),
    "borrow": ("Động từ", "/ˈbɑːroʊ/", "Vay, mượn (được sự cho phép và sẽ trả lại)"),
    "damage": ("Danh từ / Động từ", "/ˈdæmɪdʒ/", "Hư hại, tổn hại, làm hư hỏng"),
    "hint": ("Danh từ", "/hɪnt/", "Gợi ý, lời mách nước khéo léo"),
    "leak": ("Danh từ / Động từ", "/liːk/", "Chỗ rò rỉ, chảy nước ra ngoài"),
    "replacement part": ("Cụm danh từ", "/rɪˈpleɪsmənt pɑːrt/", "Phụ tùng, linh kiện thay thế"),
    "replacement parts": ("Cụm danh từ", "/rɪˈpleɪsmənt pɑːrts/", "Các phụ tùng thay thế"),
    "check": ("Động từ", "/tʃek/", "Kiểm tra kỹ lưỡng"),
    "handyman": ("Danh từ", "/ˈhændimæn/", "Thợ sửa vặt, người khéo tay chữa đồ gia dụng"),
    "home repairs": ("Cụm danh từ", "/hoʊm rɪˈperz/", "Công việc sửa chữa nhà cửa"),
    "redecorate": ("Động từ", "/ˌriːˈdekəreɪt/", "Sơn sửa, trang trí lại nhà cửa"),
    "repair": ("Động từ / Danh từ", "/rɪˈper/", "Sửa chữa, khắc phục hỏng hóc"),
    "furnace": ("Danh từ", "/ˈfɜːrnɪs/", "Lò sưởi, hệ thống sưởi trung tâm trong nhà"),

    # Unit 5
    "bothersome": ("Tính từ", "/ˈbɑːðərsəm/", "Phiền toái, gây phiền hà quấy rầy"),
    "deserted": ("Tính từ", "/dɪˈzɜːrtɪd/", "Vắng tanh, không một bóng người"),
    "elegant": ("Tính từ", "/ˈelɪɡənt/", "Thanh lịch, trang nhã, tao nhã"),
    "glamorous": ("Tính từ", "/ˈɡlæmərəs/", "Hào nhoáng, quyến rũ lộng lẫy"),
    "polite": ("Tính từ", "/pəˈlaɪt/", "Lịch thiệp, lễ phép, nhã nhặn"),
    "tiny": ("Tính từ", "/ˈtaɪni/", "Cực kỳ nhỏ bé, tí hon"),
    "deep": ("Tính từ", "/diːp/", "Trầm, sâu lắng (giọng nói / âm thanh)"),
    "disappointed": ("Tính từ", "/ˌdɪsəˈpɔɪntɪd/", "Thất vọng, buồn chán vì không như ý"),
    "full": ("Tính từ", "/fʊl/", "Dày dặn, vang ấm, đầy đặn (chất giọng)"),
    "loud": ("Tính từ", "/laʊd/", "To tiếng, ồn ào"),
    "rude": ("Tính từ", "/ruːd/", "Thô lỗ, bất lịch sự, hỗn xược"),
    "tough": ("Tính từ", "/tʌf/", "Khó khăn, gian khổ, dai sức"),

    # Unit 6
    "wealthy": ("Tính từ", "/ˈwelθi/", "Giàu có, sung túc, nhiều của cải"),
    "satisfied": ("Tính từ", "/ˈsætɪsfaɪd/", "Mãn nguyện, bằng lòng, hài lòng"),
    "limited budget": ("Cụm danh từ", "/ˈlɪmɪtɪd ˈbʌdʒɪt/", "Ngân sách hạn hẹp, eo hẹp tiền bạc"),
    "short of cash": ("Cụm tính từ", "/ʃɔːrt əv kæʃ/", "Tạm thời thiếu tiền mặt, kẹt tiền"),
    "purchase": ("Động từ / Danh từ", "/ˈpɜːrtʃəs/", "Mua sắm, giao dịch mua hàng"),
    "installments": ("Danh từ số nhiều", "/ɪnˈstɔːlmənts/", "Các khoản tiền trả góp định kỳ"),
    "get your money's worth": ("Thành ngữ", "/ɡet jɔːr ˈmʌni wɜːrθ/", "Đáng đồng tiền bát gạo, nhận giá trị xứng đáng"),
    "affordable": ("Tính từ", "/əˈfɔːrdəbl/", "Vừa túi tiền, giá cả có thể chi trả được"),

    # Unit 7
    "the vote is in": ("Thành ngữ", "/ðə voʊt ɪz ɪn/", "Kết quả kiểm phiếu đã có đầy đủ"),
    "candidate": ("Danh từ", "/ˈkændɪdeɪt/", "Ứng cử viên tranh cử"),
    "defeat": ("Động từ / Danh từ", "/dɪˈfiːt/", "Đánh bại đối thủ / sự thất bại"),
    "election": ("Danh từ", "/ɪˈlekʃn/", "Cuộc bầu cử, đợt bỏ phiếu"),
    "lead in the polls": ("Thành ngữ", "/liːd ɪn ðə poʊlz/", "Dẫn đầu trong các cuộc thăm dò ý kiến"),
    "politics": ("Danh từ", "/ˈpɑːlətɪks/", "Chính trị, công việc chính trường"),
    "poll": ("Danh từ / Động từ", "/poʊl/", "Cuộc thăm dò dư luận / phòng bỏ phiếu"),
    "run for office": ("Thành ngữ", "/rʌn fər ˈɔːfɪs/", "Ra tranh cử vào một chức vụ công quyền"),
    "vote": ("Động từ / Danh từ", "/voʊt/", "Bỏ phiếu / lá phiếu bầu"),
    "campaign": ("Danh từ", "/kæmˈpeɪn/", "Chiến dịch vận động tranh cử"),
    "controversial issues": ("Cụm danh từ", "/ˌkɑːntrəˈvɜːrʃl ˈɪʃuːz/", "Những vấn đề còn nhiều tranh cãi"),
    "press conference": ("Cụm danh từ", "/ˈpres ˌkɑːnfərəns/", "Buổi họp báo chính thức"),
    "chances": ("Danh từ số nhiều", "/ˈtʃænsɪz/", "Cơ hội, khả năng thành công"),
    "elect": ("Động từ", "/ɪˈlekt/", "Bầu chọn, trúng cử"),
    "party": ("Danh từ", "/ˈpɑːrti/", "Đảng phái chính trị"),
    "election results": ("Cụm danh từ", "/ɪˈlekʃn rɪˈzʌlts/", "Kết quả cuộc bầu cử"),
    "voters": ("Danh từ số nhiều", "/ˈvoʊtərz/", "Các cử tri tham gia bỏ phiếu"),

    # Unit 8
    "arson": ("Danh từ", "/ˈɑːrsn/", "Tội cố ý phóng hỏa đốt nhà/tài sản"),
    "clue": ("Danh từ", "/kluː/", "Manh mối, gợi ý phá án"),
    "evidence": ("Danh từ", "/ˈevɪdəns/", "Chứng cứ, bằng chứng pháp lý"),
    "inspection": ("Danh từ", "/ɪnˈspekʃn/", "Sự thanh tra, giám định kỹ lưỡng"),
    "open an investigation": ("Thành ngữ", "/ˈoʊpən ən ɪnˌvestɪˈɡeɪʃn/", "Mở một cuộc điều tra chính thức"),
    "suspicion": ("Danh từ", "/səˈspɪʃn/", "Sự nghi ngờ, mối hoài nghi"),
    "attempted": ("Tính từ", "/əˈtemptɪd/", "Bất thành (nỗ lực phạm tội nhưng không trót lọt)"),
    "commit": ("Động từ", "/kəˈmɪt/", "Phạm (tội lỗi, hành vi trái luật)"),
    "illegal": ("Tính từ", "/ɪˈliːɡl/", "Bất hợp pháp, vi phạm pháp luật"),
    "murder": ("Danh từ / Động từ", "/ˈmɜːrdər/", "Tội giết người, sát hại"),
    "suspect": ("Danh từ / Động từ", "/ˈsʌspekt/ - /səˈspekt/", "Nghi phạm / nghi ngờ"),
    "threat": ("Danh từ", "/θret/", "Lời đe dọa, hiểm họa"),

    # Unit 9
    "recycle": ("Động từ", "/ˌriːˈsaɪkl/", "Tái chế rác thành nguyên liệu mới"),
    "upcycle": ("Động từ", "/ˈʌpsaɪkl/", "Tái chế sáng tạo thành đồ cao cấp hơn"),
    "reuse": ("Động từ", "/ˌriːˈjuːz/", "Tái sử dụng nguyên trạng"),
    "biodegradable": ("Tính từ", "/ˌbaɪoʊdɪˈɡreɪdəbl/", "Có thể phân hủy sinh học tự nhiên"),
    "landfill": ("Danh từ", "/ˈlændfɪl/", "Bãi chôn lấp rác thải tập trung"),
    "sorting": ("Danh từ", "/ˈsɔːrtɪŋ/", "Việc phân loại rác thải tại nguồn"),
    "waste": ("Danh từ", "/weɪst/", "Rác thải, chất thải"),
    "natural resources": ("Cụm danh từ", "/ˈnætʃrəl ˈriːsɔːrsɪz/", "Tài nguyên thiên nhiên"),
    "hands-on": ("Tính từ", "/ˌhændz ˈɑːn/", "Thực hành thực tế, bắt tay vào làm"),
    "workshop": ("Danh từ", "/ˈwɜːrkʃɑːp/", "Buổi hội thảo chuyên đề, xưởng thực hành"),

    # Unit 10
    "documentary": ("Danh từ", "/ˌdɑːkjuˈmentri/", "Bộ phim tài liệu"),
    "film festival": ("Cụm danh từ", "/fɪlm ˈfestɪvl/", "Liên hoan phim điện ảnh"),
    "film set": ("Cụm danh từ", "/fɪlm set/", "Phim trường, trường quay đóng phim"),
    "movie industry": ("Cụm danh từ", "/ˈmuːvi ˈɪndəstri/", "Ngành công nghiệp điện ảnh"),
    "film school": ("Cụm danh từ", "/fɪlm skuːl/", "Trường đào tạo điện ảnh chuyên nghiệp"),
    "digital technology": ("Cụm danh từ", "/ˈdɪdʒɪtl tekˈnɑːlədʒi/", "Công nghệ kỹ thuật số"),
    "cinematography": ("Danh từ", "/ˌsɪnəməˈtɑːɡrəfi/", "Nghệ thuật quay phim điện ảnh"),
    "special effects": ("Cụm danh từ", "/ˌspeʃl ɪˈfekts/", "Hiệu ứng kỹ xảo đặc biệt"),
    "independent films": ("Cụm danh từ", "/ˌɪndɪˈpendənt fɪlmz/", "Các dòng phim độc lập (kinh phí tự túc)"),

    # Intermediate 3 - Unit 1
    "get engaged": ("Cụm động từ", "/ɡet ɪnˈɡeɪdʒd/", "Đính hôn, đính ước chuẩn bị cưới"),
    "easygoing": ("Tính từ", "/ˌiːziˈɡoʊɪŋ/", "Dễ tính, hòa đồng, thoải mái"),
    "affectionate": ("Tính từ", "/əˈfekʃənət/", "Giàu tình cảm, âu yếm vỗ về"),
    "in love with": ("Thành ngữ", "/ɪn lʌv wɪð/", "Phải lòng ai, đang yêu say đắm"),
    "get used to": ("Thành ngữ", "/ɡet juːst tuː/", "Dần quen với cái gì mới lạ"),
    "tease": ("Động từ", "/tiːz/", "Trêu chọc, chọc ghẹo ai đó"),
    "get divorced": ("Cụm động từ", "/ɡet dɪˈvɔːrst/", "Ly hôn, chấm dứt hôn nhân"),
    "divorced": ("Tính từ", "/dɪˈvɔːrst/", "Đã ly hôn"),
    "sense of humor": ("Cụm danh từ", "/sens əv ˈhjuːmər/", "Khiếu hài hước, óc hóm hỉnh"),
    "flirt": ("Động từ", "/flɜːrt/", "Tán tỉnh, đưa đẩy đùa cợt"),
    "spending time": ("Cụm động từ", "/ˈspendɪŋ taɪm/", "Dành thời gian ở cạnh ai"),
    "blind date": ("Cụm danh từ", "/ˌblaɪnd ˈdeɪt/", "Cuộc hẹn hò người chưa từng gặp gỡ"),
    "embrace": ("Động từ / Danh từ", "/ɪmˈbreɪs/", "Ôm ghì, đón nhận tình cảm nồng ấm"),

    # Intermediate 3 - Unit 2
    "condition": ("Danh từ", "/kənˈdɪʃn/", "Thể lực, thể trạng sức khỏe"),
    "well-equipped": ("Tính từ", "/ˌwel ɪˈkwɪpt/", "Được trang bị đầy đủ dụng cụ tối tân"),
    "finals": ("Danh từ số nhiều", "/ˈfaɪnlz/", "Loạt trận đấu chung kết tranh chức vô địch"),
    "give in": ("Cụm động từ", "/ɡɪv ɪn/", "Nhượng bộ, chịu thua, đầu hàng"),
    "team spirit": ("Cụm danh từ", "/tiːm ˈspɪrɪt/", "Tinh thần đồng đội gắn kết"),
    "weight lifting": ("Cụm danh từ", "/ˈweɪt ˌlɪftɪŋ/", "Bộ môn cử tạ, thể hình cơ bắp"),
    "make a name for yourself": ("Thành ngữ", "/meɪk ə neɪm fər jɔːrˈself/", "Tạo dựng tên tuổi lừng lẫy, thành danh"),
    "in shape": ("Thành ngữ", "/ɪn ʃeɪp/", "Vóc dáng cân đối, thể lực sung mãn"),
    "handle an upset": ("Thành ngữ", "/ˈhændl ən ˈʌpset/", "Đương đầu và vượt qua sự cố bất ngờ/thất bại cay đắng"),
    "build up your strength": ("Thành ngữ", "/bɪld ʌp jɔːr streŋkθ/", "Rèn luyện tăng cường sức mạnh thể chất"),
    "at your own pace": ("Thành ngữ", "/æt jɔːr oʊn peɪs/", "Theo nhịp độ riêng phù hợp với mình"),
    "exhausted": ("Tính từ", "/ɪɡˈzɔːstɪd/", "Mệt lử, kiệt sức sau trận đấu"),

    # Intermediate 3 - Unit 3
    "empty promise": ("Cụm danh từ", "/ˈempti ˈprɑːmɪs/", "Lời hứa suông vô giá trị"),
    "handle the situation": ("Thành ngữ", "/ˈhændl ðə ˌsɪtʃuˈeɪʃn/", "Kiểm soát và giải quyết ổn thỏa tình thế"),
    "go on strike": ("Thành ngữ", "/ɡoʊ ɑːn straɪk/", "Tổ chức đình công, bãi công"),
    "productive": ("Tính từ", "/prəˈdʌktɪv/", "Đạt năng suất lao động cao, hiệu quả"),
    "quit": ("Động từ", "/kwɪt/", "Từ chức, thôi việc, bỏ cuộc"),
    "wage increase": ("Cụm danh từ", "/weɪdʒ ˈɪnkriːs/", "Sự tăng mức lương căn bản"),
    "make a living": ("Thành ngữ", "/meɪk ə ˈlɪvɪŋ/", "Kiếm kế sinh nhai, trang trải cuộc sống"),
    "incentives": ("Danh từ số nhiều", "/ɪnˈsentɪvz/", "Chế độ đãi ngộ, phần thưởng khích lệ"),
    "make cuts": ("Thành ngữ", "/meɪk kʌts/", "Cắt giảm ngân sách, tiết giảm chi phí"),
    "proposal": ("Danh từ", "/prəˈpoʊzl/", "Bản đề xuất phương án thương lượng"),
    "under the circumstances": ("Thành ngữ", "/ˈʌndər ðə ˈsɜːrkəmstænsɪz/", "Trong hoàn cảnh hiện tại"),
    "walk out": ("Cụm động từ", "/wɔːk aʊt/", "Rời khỏi nơi làm việc để phản đối, bãi công"),

    # Intermediate 3 - Unit 4
    "capable of": ("Cụm tính từ", "/ˈkeɪpəbl əv/", "Có năng lực, có đủ khả năng làm gì"),
    "depend on": ("Cụm động từ", "/dɪˈpend ɑːn/", "Phụ thuộc, trông cậy hoàn toàn vào"),
    "homeless": ("Tính từ", "/ˈhoʊmləs/", "Vô gia cư, không nơi nương tựa"),
    "make a difference": ("Thành ngữ", "/meɪk ə ˈdɪfrəns/", "Tạo nên sự khác biệt tích cực, thay đổi tình hình"),
    "manage by yourself": ("Thành ngữ", "/ˈmænɪdʒ baɪ jɔːrˈself/", "Tự mình xoay xở giải quyết mà không cần ai giúp"),
    "mange by yourself": ("Thành ngữ", "/ˈmænɪdʒ baɪ jɔːrˈself/", "Tự mình xoay xở giải quyết mà không cần ai giúp"),
    "senior citizen": ("Cụm danh từ", "/ˌsiːniər ˈsɪtɪzn/", "Người cao tuổi (từ 65 tuổi trở lên)"),
    "senior citizens": ("Cụm danh từ", "/ˌsiːniər ˈsɪtɪznz/", "Các cụ già, người cao tuổi"),
    "establishment": ("Danh từ", "/ɪˈstæblɪʃmənt/", "Giới cầm quyền, tầng lớp đầu não thể chế"),
    "housing alternatives": ("Cụm danh từ", "/ˈhaʊzɪŋ ɔːlˈtɜːrnətɪvz/", "Các giải pháp nhà ở thay thế cho người nghèo"),
    "on the streets": ("Thành ngữ", "/ɑːn ðə striːts/", "Sống vạ vật đầu đường xó chợ, không nhà"),
    "pay the rent": ("Thành ngữ", "/peɪ ðə rent/", "Thanh toán tiền thuê nhà hàng tháng"),
    "take steps": ("Thành ngữ", "/teɪk steps/", "Tiến hành các bước hành động cụ thể"),

    # Intermediate 3 - Unit 5
    "concentrate on": ("Cụm động từ", "/ˈkɑːnsntreɪt ɑːn/", "Tập trung cao độ vào điều gì"),
    "heart attack": ("Cụm danh từ", "/ˈhɑːrt əˌtæk/", "Cơn nhồi máu cơ tim cấp"),
    "limit": ("Động từ / Danh từ", "/ˈlɪmɪt/", "Giới hạn, hạn chế mức dung nạp"),
    "overweight": ("Tính từ", "/ˌoʊvərˈweɪt/", "Thừa cân so với chuẩn sức khỏe"),
    "small quantities": ("Cụm danh từ", "/smɔːl ˈkwɑːntətiz/", "Khẩu phần ăn lượng nhỏ, khẩu phần vừa phải"),
    "weigh yourself": ("Cụm động từ", "/weɪ jɔːrˈself/", "Tự bước lên cân để theo dõi trọng lượng"),
    "eat sensibly": ("Thành ngữ", "/iːt ˈsensəbli/", "Ăn uống điều độ, lựa chọn thực phẩm lành mạnh"),
    "heart condition": ("Cụm danh từ", "/ˈhɑːrt kənˌdɪʃn/", "Bệnh lý tim mạch mãn tính"),
    "nutritious": ("Tính từ", "/nuːˈtrɪʃəs/", "Bổ dưỡng, giàu dinh dưỡng cho cơ thể"),
    "palpitations": ("Danh từ số nhiều", "/ˌpælpɪˈteɪʃnz/", "Chứng đánh trống ngực, tim đập thình thịch bất thường"),
    "sweating": ("Danh từ / Động từ", "/ˈswetɪŋ/", "Hiện tượng đổ mồ hôi đầm đìa"),
    "whole-grain": ("Tính từ", "/ˌhoʊl ˈɡreɪn/", "Nguyên cám, làm từ hạt ngũ cốc nguyên vỏ"),
}
