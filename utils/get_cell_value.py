import math


def get_cell_value(row, cell_name):
  val = getattr(row, cell_name)

  if isinstance(val, float) and not math.isnan(val):
    val = int(val)

  if cell_name == 'partner_phone' or cell_name == 'partner_private_phone' and not str(val).startswith("+"):
    val = '+' + str(val)

  return val