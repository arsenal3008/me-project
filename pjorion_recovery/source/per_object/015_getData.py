# recovered via pycdc

if not self.isBlack():
    
    try:
        f = open(file_lic, 'r')
        lines = f.readlines()
        f.close()
        for txt in lines:
            txt = txt.replace('\n', '')
            
            try:
                (q_hash, date) = txt.split(',')
            ID = self.getID()
            cpmTxt = self.getHash('zjFL%s' % ID + date)
            if cpmTxt == q_hash:
                q_hash = self.getHash('zjID%s' % ID)
                return (q_hash, date, '1')
            cpmTxt = None.getHash('zjFLdemotodate' + date)
            if cpmTxt == q_hash:
                STATUS = 'Demo'
                q_hash = self.getHash('zjID%s' % ID)
                return (q_hash, date, '0')
            cpmTxt = None.getHash('zjFLtrialtodate' + date)
            if cpmTxt == q_hash:
                STATUS = 'Trial'
                q_hash = self.getHash('zjID%s' % ID)
                return (q_hash, date, '2')
            cpmTxt = None.getHash('zjFLtesttodate2' + date)
            if cpmTxt == q_hash:
                STATUS = 'Test'
                q_hash = self.getHash('zjID%s' % ID)
                return (q_hash, date, '3')
            continue
            return None
            except Exception:
                err = None
                continue
