
from __future__ import division
from bluesolver.utility.errors import EquationFormationError, SolverError
from decimal import Decimal as decimal

class Equation(object):
    def __init__(self, equation_text, variable_list):
        from math import Symbol, Eq, sqrt, log, pi, sin, cos
        
        self.equation_text = equation_text
        self.variable_list = variable_list
        
        try:
            #Execute code to bind symbol objects to variable names.
            for variable in variable_list:          
                exec variable + ' = Symbol(\'' + variable + '\')' in locals()
            
            #Format equation and attach to mathematical equation object.           
            self.equation_object = eval('Eq(' + self._format_equation(self.equation_text) + ')')
        except:
            raise EquationFormationError(equation_text + ": did not initialize correctly, check the variable list.\n" + str(variable_list))
    
    def solve_generic(self, variable_symbol):
        import math 
        from math import sqrt, log, pi, sin, cos
        variable = eval('math.simplify(math.Symbol(\'' + variable_symbol + '\'))')
        
        solution = math.solve(self.equation_object, variable)[0]
        return variable_symbol + ' = ' + self._unformat_equation(str(solution))
    
    def solve(self, variable_data_list):
        import math
        from math import sqrt, log, pi, sin, cos
        
        # Initialize the list of variable data so that it can be consumed by the
        # solver engine.
        calc_data = {}
        for variable in variable_data_list:
            if variable.value is not None:
                calc_data[variable.symbol] = variable.value * variable.conversion
            else:
                symbol_string = 'math.Symbol(\'' + variable.symbol + '_conv\')'
                calc_data[variable.symbol + '_conv'] = symbol_string
                calc_data[variable.symbol] = str(variable.conversion) + '*' + variable.symbol + '_conv'
        
        # Preferably a sorted dictionary could be used here.
        # This must be done to ensure that conversion variables are
        # not used before they are bound.
        for variable in sorted(calc_data.keys(), reverse=True): 
            exec variable + ' = ' + str(calc_data[variable]) in locals()
        
        eq = eval('math.Eq(' + self._format_equation(self.equation_text) + ')')    
        
        results = {}
        for variable in variable_data_list:
            if variable.value is not None:
                results[variable.symbol] = variable.value
            else:
                solutions = eval('math.solve(eq, ' + variable.symbol + '_conv)')
                solution = self.validate_solutions(solutions)
                results[variable.symbol] = solution
        
        return results
  
    def validate_solutions(self, solutions):
        if len(solutions) == 1:
            try: 
                float(solutions[0])
                return solutions[0].evalf()
            except:
                raise SolverError('The solver could not find a real number solution.')
        if len(solutions) == 0:
            raise SolverError('The solver found no solutions.')
        
        if len(solutions) > 1:
            real_solutions = []
            for solution in solutions:
                try:
                    float(solution)
                    real_solutions.append(solution)
                except:
                    pass
            if len(real_solutions) == 0:
                raise SolverError('The solver could not find a real number solution.')
            return max([str(solution.evalf()) for solution in real_solutions])
        
        raise SolverError('The solver encountered an error.')
            
  
    @staticmethod
    def _format_equation(equation_text):
        return equation_text.replace('=', ',').replace('^', '**')
    
    @staticmethod
    def _unformat_equation(equation_math):
        return equation_math.replace(',', '=').replace('**', '^')
    
class VariableData:
    """Represents variable data. VariableData(symbol, value, units, conversions)"""
    def __init__(self, symbol, value=None, units=None, conversion=1):
        self.symbol = symbol
        self.value = value
        self.units = units
        self.conversion = conversion

