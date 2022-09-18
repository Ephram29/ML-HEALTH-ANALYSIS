from multiprocessing import parent_process


class Pedigree():
    parent_diabetic_prob=0.25
    parent_affected_prob=0.5
    total_offsprings=4

    def __init__(self, gpf, gpm, f_db, m_db, gender, db_siblings):
        self.gender=gender
        self.is_father_GP_diabetic=gpf
        self.is_mother_GP_diabetic=gpm
        self.father_diabetic=f_db
        self.mother_diabetic=m_db
        self.father_affected=False
        self.mother_affected=False
        self.diabetic_siblings=db_siblings
        self.father_chromosomes='TT'
        self.mother_chromosomes='TT'
        self.father_x_linked='XY'
        self.mother_x_linked='XX'
        self.genetic_type=None
        self.parent_chromosomes=[]#0 chromosome represents father 1 represents mother
        self.parent_xlinked=[]
        self.offsprings_xlinked=[]
        self.offsprings=[]
        self.probablity=0
    def get_parent_chromosomes(self):
        #identifying father's chromosomes
            if self.father_diabetic:
                self.father_chromosomes='tt'
                self.father_x_linked='xY'
            elif self.is_father_GP_diabetic:
                self.father_affected=True
                self.father_chromosomes='Tt'
            else:
                pass
        #identifying mother's chromosomes
            if self.mother_diabetic:
                self.mother_chromosomes='tt'
                self.mother_x_linked = 'xx'
            elif self.is_mother_GP_diabetic:
                self.mother_affected = True
                self.mother_chromosomes = 'Tt'
                self.mother_x_linked = 'Xx'
            else:
                pass
            self.parent_chromosomes.append(self.father_chromosomes)
            self.parent_chromosomes.append(self.mother_chromosomes)
            self.parent_xlinked.append(self.father_x_linked)
            self.parent_xlinked.append(self.mother_x_linked)

    def punnet_square(self,type):
        if type=="x-linked":
            parent_chromosomes = self.parent_xlinked
        else:
            parent_chromosomes = self.parent_chromosomes
        print("parent=",parent_chromosomes)
        offspings = []
        for father_c in parent_chromosomes[0]:
            for mother_c in parent_chromosomes[1]:
                offsping_gene = father_c+mother_c
                offspings.append(offsping_gene)

        if type == "x-linked":
            for i, item in enumerate(offspings):
                if item[0] != 'X':
                    reversed_item = item[::-1]
                    offspings[i] = reversed_item
        else:
            for i,item in enumerate(offspings):
                if item[0]!='T':
                    reversed_item=item[::-1]
                    offspings[i]=reversed_item
        #print(offspings.index('tt'))
        print(offspings)
        return offspings

    def has_diabetic_siblings(self):
        if self.diabetic_siblings:
            if 'Tt' in self.offsprings:
                self.offsprings.remove('Tt')
            elif 'tt' in self.offsprings:
                self.offsprings.remove('tt')
            self.total_offsprings-=1
            print("offsprings after remove=",self.offsprings)

    def offspring_diabetic_prob(self):
        result=round(self.offsprings.count('tt')/self.total_offsprings,2)
        print("p(tt)=",result)
        return result

    def offspring_affected_prob(self):
        if self.offsprings.count('Tt')==4:
            return 0.5
        result = round(self.offsprings.count('Tt')/self.total_offsprings,2)
        print("p(Tt)=", result)
        return result
    def x_linked_probablity(self):
        if self.gender=="FEMALE":
            male_x_chromosome_prob=self.father_x_linked.count('x')/1
            if self.offsprings_xlinked.count('Xx')==2:
                female_diabetic_prob=0.5
                return female_diabetic_prob
            prob_female_affected=self.offsprings_xlinked.count('Xx')/4
            prob_female_diabetic=self.offsprings_xlinked.count('xx')/2
            female_diabetic_prob=(male_x_chromosome_prob*prob_female_affected)+(male_x_chromosome_prob*prob_female_diabetic)
            print("female x-linked=",female_diabetic_prob)
            if self.mother_affected:
                female_x_chromosome_prob=0.5 #X-linked Dominant
                female_diabetic_prob += (female_x_chromosome_prob*prob_female_affected)+(female_x_chromosome_prob*prob_female_diabetic)
                print("female x-linked=", female_diabetic_prob)
            return female_diabetic_prob
        if self.gender=="MALE":
            female_x_chromosome_prob = self.mother_x_linked.count('x')/2
            #print("female x-linked chrom=",female_x_chromosome_prob)
            prob_male_diabetic = self.offsprings_xlinked.count('xY')/2
            male_diabetic_prob = (female_x_chromosome_prob*prob_male_diabetic)
            print("male x-linked=", male_diabetic_prob)
            return male_diabetic_prob


    def determine_type_probab(self): #autosomal recessive or dominant
        if not self.father_diabetic and not self.mother_diabetic:
            self.genetic_type="AUTOSOMAL RECESSIVE"
            probab=0.25
        elif self.father_diabetic or self.mother_diabetic:
            self.genetic_type="AUTOSOMAL DOMINANT"
            probab=0.5
        #print("probablity dia=", self.offspring_diabetic_prob())
        #print("probablity affected=", self.offspring_affected_prob())
        if self.offspring_diabetic_prob()==1:
            final_probab=1
        else:
            final_probab = probab+(self.parent_diabetic_prob*self.offspring_diabetic_prob())+(self.parent_affected_prob*self.offspring_affected_prob())
        print("probablity autosomal=",final_probab)
        final_probab*=self.x_linked_probablity()
        print("probablity final=", round(final_probab,3))
        self.probablity = round(final_probab, 3)



