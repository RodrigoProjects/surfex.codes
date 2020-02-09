from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import re
import pprint
import os
import json

class UM_Schedule_API():

    def __init__(self, chromedriver_path : str = None):
        self.options = webdriver.ChromeOptions(); 
        self.options.add_argument('headless') # Sem abrir o browser.
        self.options.add_experimental_option('excludeSwitches', ['enable-logging']) # Sem notificações de progresso.        
        self.pp = pprint.PrettyPrinter() # Objeto PrettyPrinter
        self.chrome_path = chromedriver_path

    def __roman2Int(self, s : str):
        rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        int_val = 0
        for i in range(len(s)):
            if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
                int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
            else:
                int_val += rom_val[s[i]]
        return int_val

    def get(self, CURSO : str = 'Mestrado Integrado em Engenharia Informática', ANO : int = 3, force_update : bool = False):
        
        sigla = ''.join(re.findall('[A-Z]', CURSO))
        
        json_path = f'{sigla}_{ANO}.json'

        if os.path.exists(f'./horarios/{json_path}') and not force_update:
            return json.load(open(f'./horarios/{json_path}', encoding='utf8'))
        
        try:
            driver = webdriver.Chrome(options=self.options) if self.chrome_path == None else webdriver.Chrome(self.chrome_path,options=self.options)

            driver.get('https://alunos.uminho.pt/PT/estudantes/Paginas/InfoUteisHorarios.aspx')
            search_bar = driver.find_element_by_class_name('rcbInput')
            search_button = driver.find_element_by_id('ctl00_ctl40_g_e84a3962_8ce0_47bf_a5c3_d5f9dd3927ef_ctl00_btnSearchHorario')

            search_bar.send_keys(CURSO)
            search_button.click()

            year_selector = driver.find_element_by_id(f'ctl00_ctl40_g_e84a3962_8ce0_47bf_a5c3_d5f9dd3927ef_ctl00_dataAnoCurricular_{ANO - 1}')
            year_selector.click()

            schedule_expand = driver.find_element_by_id('ctl00_ctl40_g_e84a3962_8ce0_47bf_a5c3_d5f9dd3927ef_ctl00_chkMostraExpandido')
            schedule_expand.click()

            uc_table = driver.find_element_by_class_name('rsContentTable')
            table_rows = uc_table.find_elements_by_tag_name('tr')[::2]

            hour = 9
            day = 0
            week_days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex']
            horario_dict = { day: [] for day in week_days}

            for tr in table_rows:
                tds = tr.find_elements_by_tag_name('td')
                for td in tds:
                    if len(td.text) > 2:
                        for uc in td.find_elements_by_css_selector(".rsApt.rsAptSimple"):
                            text = str(uc.get_attribute("title"))
                            uc_name = list(filter(lambda x: str.isupper(x[0]), text.split('\n')[0].split()))
                            
                            uc_name[-1] = str(self.__roman2Int(uc_name[-1])) if str.isupper(uc_name[-1]) and uc_name[-1][0] in ['I','V','X','C'] else uc_name[-1]

                            uc_turno = re.findall('[PT][PL0-9]*', text)[-1]
                            uc_edificio = re.findall(' [0-9] ', text)[0].replace(' ','')
                            uc_sala = re.findall('[0-9]\.[0-9][0-9]', text)[0]
                            duracao = int(round(uc.size["height"] / 116, 0))
                            info = {'hora_de_inicio' : hour, 'nome' : ' '.join(uc_name), 'sigla': ''.join(list(map(lambda x: x[0], uc_name))), 'turno' : uc_turno, 'edificio' : f'CP{uc_edificio}' if uc_edificio != 7 else 'DI', 'sala' : uc_sala,'duracao' : duracao }
                            horario_dict[week_days[day]].append(info)
                    
                    day +=1
                hour +=1
                day = 0

        
        except NoSuchElementException:
            return {'error' : 'Algo foi alterado nos id\'s, classes, etc... do site dos horários.'}

        except WebDriverException:
            return {'error' : 'Caminho para o webdriver errado ou má instalação do mesmo.'}

        except Exception as e:
            print('Algo correu mal ao procurar o curso e o ano! Por favor verifique se o curso e o ano existem.')
            return {'error' : e}

        json.dump(horario_dict, open(f'./horarios/{json_path}', 'w', encoding='utf8'), indent=4)
        return horario_dict
    
    def pprint(self, dict : {}):
        self.pp.pprint(dict)

    def isCurso(self, CURSO : str):
        try:
            
            driver = webdriver.Chrome(options=self.options) if self.chrome_path == None else webdriver.Chrome(self.chrome_path,options=self.options)

            driver.get('https://alunos.uminho.pt/PT/estudantes/Paginas/InfoUteisHorarios.aspx')
            search_bar = driver.find_element_by_class_name('rcbInput')
            search_button = driver.find_element_by_id('ctl00_ctl40_g_e84a3962_8ce0_47bf_a5c3_d5f9dd3927ef_ctl00_btnSearchHorario')

            search_bar.send_keys(CURSO)
            search_button.click()

            year_selector = driver.find_element_by_id(f'ctl00_ctl40_g_e84a3962_8ce0_47bf_a5c3_d5f9dd3927ef_ctl00_dataAnoCurricular_1')

        except NoSuchElementException:
            return False

        except WebDriverException:
            return {'error' : 'Caminho para o webdriver errado ou má instalação do mesmo.'}

        except Exception as e:
            raise e


        return True        
    
    def getAll(self, value : str, CURSO : str = 'Mestrado Integrado em Engenharia Informática', ANO : int = 3):
        
        horario = self.get(CURSO, ANO)
        ret = set() 

        available_values = ['sigla', 'nome','turno']

        if value not in available_values:
            return {'error' : f'Insira um value entre {", ".join(available_values[0:len(available_values)-1])} e {available_values[-1]}'}

        for day in list(horario.values()):
            for aula in day:
                ret.add(aula[value])

        return ret

    def getCursos(self):
        pass