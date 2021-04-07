function epigram(sen)
{
  var sen_len = sen.length;
  var consonants_sum = 0;
  var vowels_sum = 0;
  for(var i = 0; i < sen_len; i++)
  {
    var x = sen[i].toUpperCase();
    if(sen[i] != ":" && sen[i] != "." && sen[i] !="," && sen[i] != "\"" && sen[i] != "\'" && sen[i] != " ")
    {
        if(x == "A" || x == "E" || x == "I" || x == "O" || x == "U" )
        {
            vowels_sum += sen[i].charCodeAt(0);
        } else {
            console.log(">>>>", sen[i], sen[i].charCodeAt(0));
            consonants_sum += sen[i].charCodeAt(0);
        }
    }
  }
  return consonants_sum - vowels_sum;
}
function fibonacci(a, b, i, sum)
 {
  
  if(b > 10000)
  {
    return sum
  } else {
   if(b % 2 != 0)
    {
      sum += b;
    }	
    return fibonacci(b, a + b, ++i, sum)
  }
}
function sum(number)
{
  var sum = 0;
  for(var i = 0; i < number; i++)
  {
    var origin_str = i.toString();
    var char_array = origin_str.split("");
    var reverse_array = char_array.reverse();
    var reverse_str = reverse_array.join("");
    if( origin_str == reverse_str)
    {
      sum += i;      
    }
  }
  return sum;
}
console.log(epigram("Dealing with failure is easy: Work hard to improve. Success is also easy to handle: You've solved the wrong problem. Work hard to improve."));