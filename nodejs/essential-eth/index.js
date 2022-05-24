import { etherToGwei } from 'essential-eth';
import { solidityKeccak256 } from 'essential-eth';

console.log(etherToGwei('10').toString());
const types = ['string', 'bool', 'uint32'];
const values = ['essential-eth is great', true, 14];
let keccak256 = solidityKeccak256(types, values);
console.log(keccak256.toString());
