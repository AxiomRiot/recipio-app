import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from parser import RecipeParser

ingredients = [
  "½ cup oil (divided)",
  "1-2 fresh Thai bird chili peppers (thinly sliced)",
  "6-8 dried red chilies (roughly chopped)",
  "1/2- 1 1/2 tablespoons Sichuan peppercorns",
  "3 tablespoons ginger (finely minced)",
  "3 tablespoons garlic (finely minced)",
  "8 ounces ground pork",
  "1-2 tablespoons spicy bean sauce (depending on your desired salt/spice levels)",
  "2/3 cup low sodium chicken broth (or water)",
  "1 pound silken tofu (cut into 1 inch/2.5cm cubes)",
  "1/4 cup water",
  "1 1/2 teaspoons cornstarch",
  "1/4 teaspoon sesame oil (optional)",
  "1/4 teaspoon sugar (optional)",
  "1 scallion (finely chopped)"
]


class TestParseIngredientList(unittest.TestCase):
  def setUp(self):
    self.parser = RecipeParser()

  def test_resolve_scraper_value_handles_method_style_access(self):
    class FakeScraper:
      def ingredients(self):
        return ["1 cup flour"]

      def title(self):
        return "Test Recipe"

    scraper = FakeScraper()
    self.assertEqual(self.parser._resolve_scraper_value(scraper, "ingredients"), ["1 cup flour"])
    self.assertEqual(self.parser._resolve_scraper_value(scraper, "title"), "Test Recipe")

  def test_parses_every_ingredient(self):
    parsed = self.parser.parse_ingredient_list(ingredients)
    self.assertEqual(len(parsed), len(ingredients))

  def test_unicode_vulgar_fraction(self):
    result = self.parser.parse_ingredient_list(["½ cup oil (divided)"])[0]
    self.assertEqual(result.quantity, 0.5)
    self.assertEqual(result.unit, "cup")
    self.assertEqual(result.name, "oil (divided)")

  def test_integer_range_is_averaged(self):
    result = self.parser.parse_ingredient_list(["1-2 fresh Thai bird chili peppers (thinly sliced)"])[0]
    self.assertEqual(result.quantity, 1.5)
    self.assertIsNone(result.unit)
    self.assertEqual(result.name, "fresh Thai bird chili peppers (thinly sliced)")

  def test_fraction_to_mixed_number_range(self):
    result = self.parser.parse_ingredient_list(["1/2- 1 1/2 tablespoons Sichuan peppercorns"])[0]
    self.assertEqual(result.quantity, 1.0)
    self.assertEqual(result.unit, "tablespoon")
    self.assertEqual(result.name, "Sichuan peppercorns")

  def test_simple_fraction(self):
    result = self.parser.parse_ingredient_list(["2/3 cup low sodium chicken broth (or water)"])[0]
    self.assertAlmostEqual(result.quantity, 2 / 3)
    self.assertEqual(result.unit, "cup")
    self.assertEqual(result.name, "low sodium chicken broth (or water)")

  def test_mixed_number(self):
    result = self.parser.parse_ingredient_list(["1 1/2 teaspoons cornstarch"])[0]
    self.assertEqual(result.quantity, 1.5)
    self.assertEqual(result.unit, "teaspoon")
    self.assertEqual(result.name, "cornstarch")

  def test_whole_number_with_unit(self):
    result = self.parser.parse_ingredient_list(["8 ounces ground pork"])[0]
    self.assertEqual(result.quantity, 8.0)
    self.assertEqual(result.unit, "ounce")
    self.assertEqual(result.name, "ground pork")

  def test_no_unit(self):
    result = self.parser.parse_ingredient_list(["1 scallion (finely chopped)"])[0]
    self.assertEqual(result.quantity, 1.0)
    self.assertIsNone(result.unit)
    self.assertEqual(result.name, "scallion (finely chopped)")


if __name__ == '__main__':
  unittest.main()
