import sys 
import ply.lex as lex
import ply.yacc as yacc


sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

tokens = [
    'CADENA',
    'ENTERO',
    'ID',
    'ASIG',
    'SUM',
    'MENORQUE',
    'MMENOS',
    'COMA',
    'NEG',
    'LPAREN',
    'RPAREN',
    'PYC',
    'PUNTO',
    'LLLAVE',
    'RLLAVE',
    'LCORCH',
    'RCORCH'
]

#Diccionario de PRs
reserved = {
    'do' : 'DO',
    'while' : 'WHILE',
    'var' : 'VAR',
    'print' : 'PRINT',
    'prompt' : 'PROMPT',
    'function' : 'FUNCTION',
    'return' : 'RETURN',
    'int' : 'INT',
    'string' : 'STRING',
    'bool' : 'BOOLEAN',
    'if' : 'IF'
    
}

#Anadimos palabras reservadas a la lista de tokens
tokens = tokens + list(reserved.values())

#Regular expression rules(SIMPLE)

t_ASIG = r'\='
t_SUM = r'\+'
t_MENORQUE = r'\<'
t_MMENOS = r'\--'
t_NEG = r'\!'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PYC = r'\;'
t_COMA = r'\,'
t_PUNTO = r'\.'
t_LLLAVE = r'\{'
t_RLLAVE = r'\}'
t_LCORCH = r'\['
t_RCORCH = r'\]'

#Regular expression rules(NOT SIMPLE)

def t_CADENA(t):
    r'\'[a-zA-Z0-9_ ]*\''
    t.value = str(t.value)
    return t

def t_ENTERO(t):    
    r'[0-9][0-9]*'
    t.value = int(t.value)
    if t.value <= 32767 and t.value >= -32767:
        return t
    print("ERROR 40: Entero mayor que 32767 o menor que -32767 no son contemplados")
    t.lexer.skip(1)

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.value = str(t.value)               
    t.type = reserved.get(t.value,'ID') #Busca si es una palabra reservada antes de generar token tipo ID, si no lo es genera token tipo ID
    return t
    
def parser(t):
    s = "<{},{}>".format(t.type, t.value)
    return s 

#T_IGNORE

t_ignore_TAB = r'\t' #TABULADOR
t_ignore_RT = r'\r'  #RETORNO DE CARRO
t_ignore_COMENTARIO = r'/\*.*?\*/'    #COMENTARIOS(/*comentario*/)

#T_ERROR
def t_error(t):
    t.lexer.skip(1)
    
###############
# Build Lexer #
###############
lexer = lex.lex()




#################################################################################################################################
#################################### Sintactico y Semantico #####################################################################
#################################################################################################################################




#############################
# Diccionarios de variables #
#############################
vars_globales = []

### ESQUEMA --> {'id': nombre,'tipo': tipo,'params':{},'vars':{}}
funciones = []

### BUFFERS ###
buffer_params = []
buffer_returns = []
buffer_vars_locales = []



########################
# Funciones auxiliares #
########################

def var_already_exist(x):
    for n in buffer_vars_locales:
        if n[0] == x:
            return True
    for n in vars_globales:
        if n[0] == x:
            return True
    
    return False

def var_is_global_int(x):
    for n in vars_globales:
        if n[0] == x and n[1] == 'int':
            return True
        
    return False

def var_is_global_bool(x):
    for n in vars_globales:
        if n[0] == x and n[1] == 'bool':
            return True
        
    return False

def var_is_global_string(x):
    for n in vars_globales:
        if n[0] == x and n[1] == 'string':
            return True

    return False

def var_is_local_int(x):
    for n in buffer_vars_locales:
        if n[0] == x and n[1] == 'int':
            return True

    return False

def var_is_local_bool(x):
    for n in buffer_vars_locales:
        if n[0] == x and n[1] == 'bool':
            return True
        
    return False

def var_is_local_str(x):
    for n in buffer_vars_locales:
        if n[0] == x and n[1] == 'string':
            return True
        
    return False

def var_is_cadena(var):
    num = 0
    for n in var:
        if n == '\'':
            num = num +1
    if num==2:
        return True
    else:
        return False   

def delete_buffer():
    l = len(buffer_params)
    while l>0:
        del buffer_params[l-1]
        l = l-1
    l = len(buffer_returns)
    while l>0:
        del buffer_returns[l-1]
        l=l-1
    l = len(buffer_vars_locales)
    while l>0:
        del buffer_vars_locales[l-1]
        l=l-1

#########
# START #
#########

def p_b_p(p):
    'P : B'
    
def p_f_p(p):
    'P : F'

#def p_eof(p):
#    'P : empty'

############################################################################################################
######################################### Function #########################################################
############################################################################################################

def p_f_function(p):
    'F : FUNCTION H ID LPAREN A RPAREN LLLAVE W RLLAVE'

    loc_vars = {}
    check = {}

    encontrado = 0
    duplicados = 0
    returns_ok = 0

    duplicado = ''
    
    #Comprobamos si el id de la funcion ya existe
    for fun in funciones:
        if fun['id'] == p[3]:
            encontrado = 1
    
    #Si no existe
    if encontrado == 0:
        #Volcamos datos de variables locales
        for n in buffer_vars_locales:
            loc_vars.setdefault(n[0],n[1])

        #Check de que no haya params duplicados
        for n in buffer_params:
            if n[0] not in check.keys():
                check.setdefault(n[0],n[1])
            else:
                duplicado = n[0]
                duplicados = 1

        #Si no hay duplicados
        #Comprobamos returns
        if p[2] != None:
            if len(buffer_returns) == 0:
                returns_ok = 1
            for n in buffer_returns:
                if n != p[2]:
                    returns_ok = 1
        else:
            for n in buffer_returns:
                if n != 'null':
                    returns_ok = 1

        #Si las dos cosas están bien
        if duplicados == 0:
            if returns_ok == 0:
                funciones.append({'id':p[3],'tipo': p[2],'params':check,'vars':loc_vars})
            else:
                print('Syntax error FUNCTION. Returns dont match with the specified type')
        #Si hay duplicados
        else:
            print('Syntax error FUNCTION. ID {} is already used as param'.format(duplicado))

    #Si existe
    else:
        print('Syntax error FUNCTION. ID {} already exists'.format(p[3]))
    
    #Limpiamos buffer
    delete_buffer()

    print(funciones)   

##### TIPO A DEVOLVER #####
def p_h_tipo(p):
    'H : T'
    p[0] = p[1]

def p_h_empty(p):
    'H : empty'
    p[0] = p[1]
##########################

##### PARAMETROS #####
def p_a_params(p):
    'A : T ID K'
    buffer_params.append([p[2],p[1]])

def p_a_empty(p):
    'A : empty'

def p_k_params(p):
    'K : COMA T ID K'
    buffer_params.append([p[3],p[2]])

def p_k_empty(p):
    'K : empty'
    
#####################

def p_w_d(p):
    'W : D W'
    

def p_w_empty(p):
    'W : empty'

def p_define_var_func(p):
    'D : VAR T ID PYC'
    if not var_already_exist(p[3]):
        buffer_vars_locales.append([p[3],p[2]])
    else:
        print('The variable already exist')

def p_d_do_while(p):
    'D : DO LLLAVE W RLLAVE WHILE LPAREN E RPAREN PYC'
    if type(p[7]) is not bool:
        print('Syntax error DO/WHILE. {} is not a bool expression'.format(p[7]))

def p_d_if(p):
    'D : IF LPAREN E RPAREN LLLAVE W RLLAVE'
    if type(p[3]) is not bool:
        print('Syntax error DO/WHILE. {} is not a bool expression'.format(p[3]))

def p_d_s(p):
    'D : S'

##########
# Return #
##########

def p_return(p):
    'W : RETURN X PYC'
    if type(p[2]) is str:
        if var_is_cadena(p[2]): 
            buffer_returns.append('string')
        elif not var_is_cadena(p[2]):    
            if var_already_exist(p[2]):
                if var_is_global_int(p[2]):
                    buffer_returns.append('int')
                elif var_is_global_bool(p[2]):
                    buffer_returns.append('bool')
                elif var_is_global_string(p[2]):
                    buffer_returns.append('string')
                elif var_is_local_int(p[2]):
                    buffer_returns.append('int')
                elif var_is_local_bool(p[2]):
                    buffer_returns.append('bool')
                elif var_is_local_str(p[2]):
                    buffer_returns.append('string')
            else:
                print('Syntax error RETURN. Variable {} is not define'.format(p[2]))
    elif type(p[2]) is int:
        buffer_returns.append('int')
    elif type(p[2]) is bool:
        buffer_returns.append('bool')    

def p_return_empty(p):
    'X : empty'
    buffer_returns.append('null')
def p_return_e(p):
    'X : E'
    p[0] = p[1]


############################################################################################################
############################################################################################################
############################################################################################################


######
# IF #
######
def p_if(p):
    'B : IF LPAREN E RPAREN LLLAVE C RLLAVE'
    if type(p[3]) is not bool:
        print('Syntax error DO/WHILE. {} is not a bool expression'.format(p[3]))


#####################
# Llamada a funcion #
#####################

def p_s_function(p):
    'S : ID LPAREN L RPAREN PYC'

def p_l_eq(p):
    'L : E Q'

def p_l_empty(p):
    'L : empty'

def p_q_eq(p):
    'Q : COMA E Q'

def p_q_empty(p):
    'Q : empty'


############
# Do While #
############

def p_do_while(p):
    'B : DO LLLAVE C RLLAVE WHILE LPAREN E RPAREN PYC'
    if type(p[7]) is not bool:
        print('Syntax error DO/WHILE. {} is not a bool expression'.format(p[7]))

def p_c_b_c(p):
    'C : B C'

def p_c_empty(p):
    'C : empty'

######################################
# Creación y asisgnación de Variable #
######################################

def p_define_var(p):
    'B : VAR T ID PYC'
    if not var_already_exist(p[3]):
        vars_globales.append([p[3],p[2]])
    else:
        print('The variable already exist')
    print(vars_globales)

def p_b_s(p):
    'B : S'
    p[0]=p[1]


def p_asig(p):
    'S : ID ASIG E PYC'
    if var_is_global_int(p[1]) or var_is_local_int(p[1]): 
        if type(p[3]) is bool:
            print('Syntax error ASIG')
        elif type(p[3]) is str:
            if var_is_cadena(p[3]):
               print('Syntax error ASIG') 
            elif not(var_is_global_int(p[3]) or var_is_local_int(p[3])):
                print('Syntax error ASIG')
            
    elif var_is_global_bool(p[1]) or var_is_local_bool(p[1]): 
        if type(p[3]) is int:
            print('Syntax error ASIG')
        elif type(p[3]) is str:
            if var_is_cadena(p[3]):
                print('Syntax error ASIG')
            if not(var_is_global_bool(p[3]) or var_is_local_bool(p[3])):
                print('Syntax error ASIG')
    
    elif var_is_global_string(p[1]) or var_is_local_str(p[3]):
        if type(p[3]) is str and not var_is_cadena(p[3]):
            if not (var_is_global_string(p[3]) or var_is_local_str(p[3])):
                print('Syntax error ASIG')
        elif type(p[3]) is bool:
            print('Syntax error ASIG')
        elif type(p[3]) is int:
            print('Syntax error ASIG')
    else:
        print('Variable {} not define'.format(p[1]))


#########
# Tipos #
#########

def p_tipo_str(p):
    'T : STRING'
    p[0] = p[1]

def p_tipo_bool(p):
    'T : BOOLEAN'
    p[0] = p[1]

def p_tipo_int(p):
    'T : INT'
    p[0] = p[1]
#def p_tipo_empty(p):
#    'T : empty'

#########
# Print #
#########

def p_print(p):
    'S : PRINT LPAREN E RPAREN PYC'
    if type(p[3]) is str:
        if not var_is_cadena(p[3]):    
            if not var_already_exist(p[3]):
                print('Syntax error PRINT. Variable {} is not define'.format(p[3]))  


#########
# Prompt #
#########

def p_prompt(p):
    'S : PROMPT LPAREN ID RPAREN PYC'  
    if not var_already_exist(p[3]):
            print('Syntax error PRINT. Variable {} is not define'.format(p[3]))   

##############
# Operadores #
##############

def p_id_mm(p):
    'S : MMENOS ID PYC'
    if not var_already_exist(p[2]):
        print('Syntax error MMINUS')
    elif not (var_is_global_int(p[2]) or var_is_local_int(p[2])):
        print('Syntax error MMINUS')

def p_e_notr(p):
    'E : NEG R'
    if type(p[2]) is bool:
        p[0] = not p[2]
    elif type(p[2]) is str and not var_is_cadena(p[2]):
        if not var_is_global_bool(p[2]):
            print('Syntax error NOT')   
    else:
        print('Syntax error NOT')

def p_e_r(p):
    'E : R'
    p[0]=p[1]

def p_erre_expression_minusthan(p):
    'R : U MENORQUE U'
    if type(p[1]) is int and type(p[3]) is int:
        p[0] = p[1] < p[3]
    elif type([1]) is int and type(p[3]) is str:
        if var_is_global_int(p[3]) or var_is_local_int(p[3]):
            p[0] = False
        else:
            print('Syntax error LESSTHAN')
    elif type(p[1]) is str and type(p[3]) is int:
        if var_is_global_int(p[1]) or var_is_local_int(p[1]):
            p[0] = False
        else:
            print('Syntax error LESSTHAN')
    elif type(p[1]) is str and type(p[3]) is str:
        if (var_is_global_int(p[1]) or var_is_local_int(p[1])) and (var_is_global_int(p[3]) or var_is_local_int(p[3])):
            p[0] = False
        else:
            print('Syntax error LESSTHAN')
    else:
        print('Syntax error LESSTHAN')

def p_erre_expression(p):
    'R : U'
    p[0] = p[1]

def p_expression_plus(p):
    'U : V SUM U'

    #Si los dos son enteros
    if type(p[1]) is int and type(p[3]) is int:
        p[0] = p[1] + p[3]

    #Si el primero es entero y el segundo id
    elif type(p[1]) is int and type(p[3]) is str:
        if var_already_exist(p[3]):
            if var_is_global_int(p[3]) or var_is_local_int(p[3]):
                p[0] = 0
            else:
                print('Variable {} is not an integer'.format(p[3]))
        else:
            print('Variable {} not define'.format(p[3]))

    #Si el primero es variable y el segundo id
    elif type(p[1]) is str and type(p[3]) is int:
        if var_already_exist(p[1]):
            if var_is_global_int(p[1]) or var_is_local_int(p[1]):
                p[0] = 0
            else:
                print('Variable {} is not an integer'.format(p[1]))
        else:
            print('Variable {} not define'.format(p[1]))

    #Si los dos son ids
    elif type(p[1]) is str and type(p[3]) is str:
        if var_already_exist(p[1]):
            if var_already_exist(p[3]):
                if var_is_global_int(p[1]) or var_is_local_int(p[1]):
                    if var_is_global_int(p[3]) or var_is_local_int(p[3]):
                        p[0] = 0
                    else:    
                        print('Variable {} is not an integer'.format(p[3]))
                else:
                    print('Variable {} is not an integer'.format(p[1]))
            else:
                print('Variable {} not define'.format(p[3]))
        else:
            print('Variable {} not define'.format(p[1]))
    else:
        print('Variables {} and {} are not integers'.format(p[1],p[3]))              

def p_expression_term(p):
    'U : V'
    p[0] = p[1]

def p_term_number(p):
    'V : ENTERO'
    p[0] = p[1]
def p_term_id(p):
    'V : ID'
    p[0] = p[1]

def p_term_string(p):
    'V : CADENA'
    p[0] = p[1]

def p_paren(p):
    'V : LPAREN E RPAREN'
    p[0]= (p[2])


####### FALTA SEMANTICO ######   
def p_v_func(p):
    'V : ID LPAREN L RPAREN'


###############
#### Empty ####
###############

def p_empty(p):
     'empty :'
     pass

###############
#### Error ####
###############

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


yacc.yacc()

while 1:
    try:
        s = raw_input('Input > ')
    except EOFError:
        break
    if not s:
        continue
    yacc.parse(s)
